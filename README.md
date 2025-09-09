# DDLC Helpers
## Decoders `.chr` Files
> Browsing this repo may spoil major plot points of [the game DDLC](https://store.steampowered.com/app/698780/Doki_Doki_Literature_Club/). I'll do my best to keep the readme clean of direct references. The actual files are not provided. If you know, you know.

## Usage
Anyway, it has one decoder for the 4 types of files in the game. It is used as follows
```sh
python main <character> <path to file>
```

Where `<character>` is the type of decoder you want to use and `<path to file>` the path to the `*.chr` file.

There is also an option to get live poem affinity values. It is still a work in progress
```sh
python main poems
```
In order to get that working you need to install [Google's Tesseract OCR Engine](https://github.com/tesseract-ocr/tesseract?tab=readme-ov-file). Here is the link to the [installation instructions](https://tesseract-ocr.github.io/tessdoc/Installation.html) you can find in the README.

Additionally, you have to add an .env file in the root of this project. Feel free to edit the [`.env.example`](./.env.example) and rename it to `.env` when you are done.
