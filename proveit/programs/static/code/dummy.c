struct node {
    int data;
    node *next;
}

int foo(int a)
{
    int x = a;
    x = x + 1;
    node * n = malloc(sizeof(node));
    n->data = x;
    assert(n->data > 0);
    return x;
}
