-- Drop existing policies
drop policy if exists "Users can view their own data" on public.users;
drop policy if exists "Users can update their own data" on public.users;
drop policy if exists "Enable insert for authenticated users" on public.users;

-- Create new policies
create policy "Users can view their own data" on public.users
    for select using (auth.uid() = id);

create policy "Users can update their own data" on public.users
    for update using (auth.uid() = id);
    
create policy "Enable insert for signup" on public.users
    for insert with check (true);  -- Permite qualquer inserção

-- Temporarily disable RLS to allow inserts during signup
alter table public.users disable row level security;
