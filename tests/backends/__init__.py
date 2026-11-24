from backends.base import (Backend, RGBImage, RGBAImage, Region, TESSELLATIONS, DISTRIBUTIONS,
                           EFFECTS, REGION_KIND)


def load_backend(name: str, python_root: str = None, c_lib: str = None) -> Backend:
    if name == "python":
        from backends.python_backend import PythonBackend
        return PythonBackend(python_root)
    if name == "c":
        from backends.c_backend import CBackend
        return CBackend(c_lib)
    raise ValueError("unknown backend: " + name)
