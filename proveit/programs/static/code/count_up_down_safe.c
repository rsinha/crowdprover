void foo(unsigned int n)
{
  unsigned int x = n;
  unsigned int y = 0;
  while(x>0)
  {
    x--;
    y++;
  }
  assert(y == n); 
}
