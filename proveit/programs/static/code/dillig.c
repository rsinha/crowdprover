void bar(unsigned int n)
{
	int i = 1;
	int j = 0;
	while(j<n)
	{
		j++;
		i += 3;
	}
	int z = i-j;
	int x = 0;
	int y = 0;
	int w = 0;
	j = 0;
	while(j<n)
	{
		z += x+y+w;
		y++;
		x += z%2;
		w += 2;
		j++;
	}
	assert(x == y);
}