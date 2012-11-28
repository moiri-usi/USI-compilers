#include <stdlib.h>
#include <assert.h>
#include "runtime.h"

/* methods */
pyobj C_m(pyobj self);
pyobj D_m(pyobj self);

/* classes */
pyobj C, D;

static void setup_classes();

int main()
{
  setup_classes();

  // c = C()
  pyobj c = create_object(C);

  // d = D()
  pyobj d = create_object(D);

  // TODO: call the __init__ method if it exists

#ifdef TAGGING
  pyobj one = inject_int(1);
#else
  pyobj one = create_int(1);
#endif

  // c.f = 1
  set_attr(c, "f", one);

  // d.f = 1
  set_attr(d, "f", one);

  pyobj i, j, k;

  // i = c.m()
  {
    pyobj meth = get_attr(c, "m");
    pyobj fun = get_function(meth);
    pyobj (*f)(pyobj) = (pyobj (*)(pyobj)) get_fun_ptr(fun);
    i = f(get_receiver(meth));
  }

  // j = d.m()
  {
    pyobj meth = get_attr(d, "m");
    pyobj fun = get_function(meth);
    pyobj (*f)(pyobj) = (pyobj (*)(pyobj)) get_fun_ptr(fun);
    j = f(get_receiver(meth));
  }

  // k = i + j
  {
#ifdef TAGGING
    // optimized, but assumes i and j are integers
    // k = i + j

    // unoptimized, but checks that i and j are integers
    k = inject_int(project_int(i) + project_int(j));
#else
    k = create_int(project_int(i) + project_int(j));
#endif
  }

  // print i, j, k
  print_any(i);
  print_any(j);
  print_any(k);
}

/* code to create classes C and D */
static void setup_classes()
{
#ifdef TAGGING
  pyobj zero = inject_int(0);
  pyobj one = inject_int(1);
#else
  pyobj zero = create_int(0);
  pyobj one = create_int(1);
#endif
  pyobj list0 = create_list(zero);
  pyobj list1 = create_list(one);

  // class C:
  //   def m(self):
  //     return self.f
  C = create_class(list0);

  // Add method m to the class.
  set_attr(C, "m", create_closure(C_m, list0));

  // class D(C):
  //   def m(self):
  //     return self.f + 1
  set_subscript(list1, zero, C); // list1[0] = C
  D = create_class(list1);

  pyobj D_m_closure = create_closure(D_m, list0);
  set_attr(D, "m", create_closure(D_m, list0));
}

/*
 * def m(self): return self.f
 */
pyobj C_m(pyobj self) {
  return get_attr(self, "f");
}

/*
 * def m(self): return self.f + 1
 */
pyobj D_m(pyobj self) {
  pyobj f = get_attr(self, "f");
  int i = project_int(f);
#ifdef TAGGING
  return inject_int(i+1);
#else
  return create_int(i+1);
#endif
}
