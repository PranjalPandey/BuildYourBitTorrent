import json
import sys
import hashlib
import bencodepy
# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"
bc = bencodepy.Bencode(encoding="utf-8")
def decode_bencode(bencoded_value):

    def extract_string(data):
        length, rest = data.split(b':',1)
        length = int(length)
        return rest[:length], rest[length:]

    def decode(data):
        if data[0:1].isdigit():
            decoded_str, rest = extract_string(data)
            return decoded_str, rest
        elif data.startswith(b'i'):
            end = data.index(b'e')
            return int(data[1:end]), data[end+1:]
        elif data.startswith(b'l'):
            data = data[1:]
            result = []
            while not data.startswith(b'e'):
                item, data = decode(data)
                result.append(item)
            return result, data[1:]
        else:
            raise ValueError("Unsupported or invalid bencoded value.")

    decoded_value, _ = decode(bencoded_value)
    return decoded_value

# Let's convert them to strings for printing to the console.
def bytes_to_str(data):
    if isinstance(data, bytes):
        return data.decode()

    raise TypeError(f"Type not serializable: {type(data)}")

def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    elif command == "info":
        torrent_file_path = sys.argv[2]
        with open(torrent_file_path, "rb") as file:
            content = file.read()
        decoded_content = bencodepy.decode(content)
        info = bytes_to_str(decoded_content)
        info_hash = hashlib.sha1(bencodepy.encode(decoded_content[b"info"])).hexdigest()
        print(f'Tracker URL: {info["announce"]}')
        print(f'Length: {info["info"]["length"]}')
        print(f"Info Hash: {info_hash}")
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
