# NowOnScreen

An app to get information about local cinema screenings.

## Requirements

- Python >= 3.10
- pip

## Setup

1. Clone the repository

```bash
git clone {repository_url}
```

2. Navigate to the project directory:

```bash
cd nowonscreen
```

3. Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

4. Create a `.env` file in the root with the following environmental variable or export it manually:

```bash
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

You can get an API key [here](https://aistudio.google.com/app/apikey).

## Usage

To run the NowOnScreen app, use the following command:

```bash
python3 nowonscreen.py [-d {today,tomorrow}] [-c {phenomena, malda, filmoteca}]
```

### Arguments

- `-d`, `--date`: Target date for the screenings. Options are `today` or `tomorrow`. If not provided, default is all week.
- `-c`, `--cinema`: Name of the cinema. Options are `phenomena`, `malda` and `filmoteca`. If not provided, default is all cinemas.

### Example

To get today's screenings at Phenomena:

```bash
python3 nowonscreen.py -d today -c phenomena
```

To get tomorrow's screenings at all cinemas:

```bash
python3 nowonscreen.py -d tomorrow
```

To get this week's screenings at Filmoteca de Catalunya:

```bash
python3 nowonscreen.py -c filmoteca
```

## Testing

To run the tests run the following command from root:

```bash
python3 tester.py
```

You can also specify the modality of example selection for the dynamic prompt (`static`, `random`, `similarity`, default is `static`):

```bash
python3 tester.py -m random
```

or

```bash
python3 tester.py --mode random
```
