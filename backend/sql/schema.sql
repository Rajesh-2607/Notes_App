-- Run this once in the Supabase SQL editor (Project -> SQL Editor -> New query)
-- for a fresh project. Safe to re-run: every statement is idempotent.

create extension if not exists vector;

-- Notes -----------------------------------------------------------------

create table if not exists public.note (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_note_user_id on public.note (user_id);

-- Chunked + embedded note content, used for RAG retrieval ---------------

create table if not exists public.note_chunk (
  id uuid primary key default gen_random_uuid(),
  note_id uuid not null references public.note (id) on delete cascade,
  chunk_index integer not null default 0,
  chunk_text text not null,
  -- Must match EMBEDDING_DIMENSIONS in backend/.env (pgvector's HNSW/IVFFlat
  -- indexes cap out at 2000 dims, so we request a reduced size from Gemini
  -- rather than its native 3072-dim output).
  embedding vector(768),
  created_at timestamptz not null default now()
);

create index if not exists idx_note_chunk_note_id on public.note_chunk (note_id);

create index if not exists idx_note_chunk_embedding on public.note_chunk
  using hnsw (embedding vector_cosine_ops);

-- Row Level Security ------------------------------------------------------
-- Enabled with no anon/authenticated policies, on purpose: the FastAPI backend
-- is the only client that ever talks to these tables, using
-- SUPABASE_SERVICE_ROLE_KEY (which bypasses RLS) after verifying the caller's
-- JWT and scoping every query by user_id itself. Leaving RLS on with no
-- policies means the tables stay inaccessible via Supabase's public REST API
-- even if the anon key ever leaks.

alter table public.note enable row level security;
alter table public.note_chunk enable row level security;

-- Vector similarity search -------------------------------------------------
-- Called from app/services/retrieval_service.py via supabase.rpc("match_notes", ...).

create or replace function match_notes(
  query_embedding vector(768),
  match_user_id uuid,
  match_count int default 3
)
returns table (
  id uuid,
  note_id uuid,
  note_title text,
  chunk_text text
)
language sql
stable
as $$
  select
    nc.id,
    nc.note_id,
    n.title as note_title,
    nc.chunk_text
  from public.note_chunk nc
  join public.note n on n.id = nc.note_id
  where n.user_id = match_user_id
    and nc.embedding is not null
  order by nc.embedding <=> query_embedding
  limit match_count;
$$;
