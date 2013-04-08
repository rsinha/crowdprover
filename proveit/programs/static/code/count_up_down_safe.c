void foo(unsigned int n)
{
  unsigned int x = n;
  unsigned int y = 0;
  while(x>0) /* loop# 1 */
  {
    x--;
    y++;
  }
  assert(y == n); 
}
