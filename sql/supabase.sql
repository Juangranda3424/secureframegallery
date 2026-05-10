create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null,
  role text not null default 'user',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint profiles_role_check
    check (role in ('user', 'supervisor', 'admin', 'visitor'))
);

create table if not exists public.albums (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text not null,
  initial_priv boolean not null default true,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint albums_title_length_check
    check (char_length(title) <= 100),
  constraint albums_description_length_check
    check (char_length(description) <= 500),
  constraint albums_status_check
    check (status in ('pending', 'approved', 'rejected'))
);

create table if not exists public.images (
  id uuid primary key default gen_random_uuid(),
  album_id uuid not null references public.albums(id) on delete cascade,
  file_path text not null,
  status text not null default 'approved',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint images_status_check
    check (status in ('approved', 'quarantined', 'rejected'))
);

create table if not exists public.image_analysis (
  id uuid primary key default gen_random_uuid(),
  image_id uuid not null references public.images(id) on delete cascade,
  analysis_type text not null,
  result text not null,
  is_suspicious boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists idx_albums_owner_id on public.albums(owner_id);
create index if not exists idx_albums_status on public.albums(status);
create index if not exists idx_images_album_id on public.images(album_id);
create index if not exists idx_images_status on public.images(status);
create index if not exists idx_image_analysis_image_id on public.image_analysis(image_id);

alter table public.profiles enable row level security;
alter table public.albums enable row level security;
alter table public.images enable row level security;
alter table public.image_analysis enable row level security;

create policy "Usuarios pueden ver su propio perfil"
on public.profiles
for select
to authenticated
using (auth.uid() = id);

create policy "Visitors pueden ver archivos"
on storage.objects
for select
to authenticated
using (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) = 'visitor'
);

create policy "Users pueden subir archivos"
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) = 'user'
);

create policy "Supervisores pueden controlar archivos"
on storage.objects
for all
to authenticated
using (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) in ('supervisor', 'admin')
)
with check (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) in ('supervisor', 'admin')
);


drop policy if exists "Usuarios pueden ver su propio perfil" on public.profiles;
drop policy if exists "Visitors pueden ver archivos" on storage.objects;
drop policy if exists "Users pueden subir archivos" on storage.objects;
drop policy if exists "Supervisores pueden controlar archivos" on storage.objects;


create policy "Usuarios pueden ver su propio perfil"
on public.profiles
for select
to authenticated
using (auth.uid() = id);

create policy "Visitors pueden ver archivos"
on storage.objects
for select
to authenticated
using (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) = 'visitor'
);

create policy "Users pueden subir archivos"
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) = 'user'
);

create policy "Supervisores pueden controlar archivos"
on storage.objects
for all
to authenticated
using (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) in ('supervisor', 'admin')
)
with check (
  bucket_id = 'galeria'
  and (select role from public.profiles where id = auth.uid()) in ('supervisor', 'admin')
);


update public.profiles
set role = 'supervisor'
where id = (
  select id
  from auth.users
  where email = 'supervisor@example.com'
);


create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  message text not null,
  type text not null default 'info',
  read boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists notifications_user_read_created_idx
on public.notifications (user_id, read, created_at desc);