from decodeYuri import analyze_base64_file
from decodeSayori import extract_qr_from_audio

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python analyze_base64.py type <file>")
    elif sys.argv[1] == "yuri":
        result = analyze_base64_file(sys.argv[2])
        print(result)
    elif sys.argv[1] == "sayori":
        result = extract_qr_from_audio(sys.argv[2])
        print(result)
    else:
        print("Usage: python analyze_base64.py type <file>")
