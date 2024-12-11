# FontMesher 🎨🖋️

Welcome to **FontMesher**! This project lets you create beautiful meshes from your favorite fonts (Currently supported fonts are listed in `style` folder, other ttf font might work, but not guaranteed - issues and contribution welcome!).

This package will use GMSH to generate a 2-D mesh with characters written on it.

## Features ✨

- **Mesh Generation**: Convert any string into a mesh using your favorite fonts.
- **Customizable**: Adjust glyph sizes, padding, and offsets to get the perfect mesh.
- **Easy to Use**: Simple API to generate and save meshes with minimal code.

## Installation 📦

Github install

```sh
git clone https://github.com/yourusername/fontmesher.git
cd fontmesher

pip install -r [requirements.txt](http://_vscodecontentref_/1)
pip install -e .
```
or via pip:
pip install 


## Usage 🚀

Generate a mesh for a string by running the demo.py script:

```sh
python demo.py "Hello, World!"
```

This will create a mesh file in the current directory.

## Example 🖼️

Here's an example of how to use the make_string_mesh function in your own code:

``` python
import os
from fontmesher import make_string_mesh, default_font

make_string_mesh(
    string="Hello, World!",
    font=default_font,
    save_dir=os.getcwd(),
    lc=0.02,
    glyph_size=0.5,
    pad_y_start=0.25,
    pad_y_end=0.25,
    pad_x_start=0.8,
    pad_x_end=0.8,
    glyph_offset=0.5,
)
```

## Contributing 🤝

We welcome contributions! Feel free to open issues or submit pull requests.

## License 📄

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements 🙏

+ Gmsh for the awesome mesh generation library.
+ FontTools for the powerful font manipulation tools.

Happy Meshing! 🎉