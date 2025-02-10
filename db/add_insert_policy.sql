-- Add insert policy
create policy "Enable insert for authenticated users" on public.users
    for insert with check (auth.uid() = id);
