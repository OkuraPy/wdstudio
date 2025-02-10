-- Drop existing table
drop table if exists public.users;

-- Create users table
create table public.users (
    id uuid references auth.users on delete cascade not null primary key,
    email text unique not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    status text default 'active' not null check (status in ('active', 'inactive'))
);

-- Enable RLS (Row Level Security)
alter table public.users enable row level security;

-- Create policies
create policy "Users can view their own data" on public.users
    for select using (auth.uid() = id);

create policy "Users can update their own data" on public.users
    for update using (auth.uid() = id);
    
create policy "Enable insert for authenticated users" on public.users
    for insert with check (auth.uid() = id);

-- Create indexes
create index users_email_idx on public.users (email);
create index users_status_idx on public.users (status);
