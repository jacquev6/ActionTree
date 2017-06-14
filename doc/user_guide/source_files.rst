.. _source_files:

Source files of examples
========================

``a.cpp``:

.. BEGIN SECTION a.cpp

.. code-block:: c++

    int main() {}

.. END SECTION a.cpp

``b.cpp``:

.. BEGIN SECTION b.cpp

.. code-block:: c++

    void b() {}

.. END SECTION b.cpp

``c.cpp``:

.. BEGIN SECTION c.cpp

.. code-block:: c++

    void c() {}

.. END SECTION c.cpp

``d.cpp``:

.. BEGIN SECTION d.cpp

.. code-block:: c++

    void d() {}

.. END SECTION d.cpp

``e.cpp``:

.. BEGIN SECTION e.cpp

.. code-block:: c++

    void e() {}

.. END SECTION e.cpp

``f.cpp``:

.. BEGIN SECTION f.cpp

.. code-block:: c++

    void f() {}

.. END SECTION f.cpp

``g.cpp``:

.. BEGIN SECTION g.cpp

.. code-block:: c++

    void g() {}

.. END SECTION g.cpp

``h.cpp``:

.. BEGIN SECTION h.cpp

.. code-block:: c++

    void h() {}

.. END SECTION h.cpp

``Makefile``:

.. BEGIN SECTION Makefile

.. code-block:: makefile

    _build/%.o: %.cpp
    	g++ -c $^ -o $@

.. END SECTION Makefile
