void bar(int n) { 
  int i;
  int sn = 0;
  i = 1;
  while(i <= n) {
    sn = sn + 2;
    i++;
  }
  assert(sn == n*2 || sn == 0);
}
