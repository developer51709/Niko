"""
=====================================================
 Astral Haven Development — Secure Zip Utility
-----------------------------------------------------
 A robust, single-file command-line tool for 
 creating and extracting ZIP archives with optional 
 exclusions and password protection.

 Designed for confidential group workflows: 
 predictable behavior, explicit error handling, and 
 minimal external dependencies.

 License: MIT License
 Copyright (c) 2026 Astral Haven Development

 Permission is hereby granted, free of charge, to 
 any person obtaining a copy of this software and 
 associated documentation files (the "Software"), to 
 deal in the Software without restriction, including 
 without limitation the rights to use, copy, modify, 
 merge, publish, distribute, sublicense, and/or sell 
 copies of the Software, and to permit persons to 
 whom the Software is furnished to do so, subject to 
 the following conditions:

 The above copyright notice and this permission 
 notice shall be included in all copies or 
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY 
 OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
 LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND 
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES 
 OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
 CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF 
 OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
 OTHER DEALINGS IN THE SOFTWARE.
=====================================================
"""

import argparse
import fnmatch
import os
import sys
import zipfile
from typing import Iterable, List, Optional


# ----------------------------------------------------------------------
# Branding / metadata
# ----------------------------------------------------------------------


TOOL_NAME = "Astral Haven Development — Secure Zip Utility"
TOOL_VERSION = "1.0.0"


def print_branding() -> None:
    print(f"\n=== {TOOL_NAME} (v{TOOL_VERSION}) ===\n")


# ----------------------------------------------------------------------
# Core functionality
# ----------------------------------------------------------------------


def _normalize_excludes(excludes: Optional[Iterable[str]]) -> List[str]:
    if not excludes:
        return []
    return [e.strip() for e in excludes if e.strip()]


def _should_exclude(path: str, excludes: List[str]) -> bool:
    if not excludes:
        return False
    # Match against basename and full relative path
    basename = os.path.basename(path)
    for pattern in excludes:
        if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(path, pattern):
            return True
    return False


def zip_directory(
    directory: str,
    output_file: str,
    exclude: Optional[Iterable[str]] = None,
    password: Optional[str] = None,
    verbose: bool = False,
) -> None:
    directory = os.path.abspath(directory)
    excludes = _normalize_excludes(exclude)

    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    output_file = os.path.abspath(output_file)
    output_dir = os.path.dirname(output_file) or os.getcwd()
    if not os.path.isdir(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    if verbose:
        print(f"[INFO] Zipping directory: {directory}")
        print(f"[INFO] Output archive: {output_file}")
        if excludes:
            print(f"[INFO] Excluding patterns: {', '.join(excludes)}")
        if password:
            print("[INFO] Password protection enabled (ZipCrypto).")

    # Ensure parent directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Use deflated compression
    with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if password:
            # Note: ZipCrypto is not strong encryption; suitable only for light protection.
            zf.setpassword(password.encode("utf-8"))

        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory)

                if _should_exclude(rel_path, excludes):
                    if verbose:
                        print(f"[SKIP] {rel_path}")
                    continue

                if verbose:
                    print(f"[ADD]  {rel_path}")
                zf.write(full_path, rel_path)

    print(f"[OK] Created ZIP archive: {output_file}")


def unzip_file(
    input_file: str,
    output_dir: str,
    password: Optional[str] = None,
    verbose: bool = False,
    overwrite: bool = False,
) -> None:
    input_file = os.path.abspath(input_file)
    output_dir = os.path.abspath(output_dir)

    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    if verbose:
        print(f"[INFO] Extracting archive: {input_file}")
        print(f"[INFO] Target directory: {output_dir}")
        if password:
            print("[INFO] Using password for extraction.")

    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(input_file, "r") as zf:
        if password:
            zf.setpassword(password.encode("utf-8"))

        for member in zf.infolist():
            target_path = os.path.join(output_dir, member.filename)

            # Prevent directory traversal attacks
            if not os.path.realpath(target_path).startswith(os.path.realpath(output_dir)):
                raise PermissionError(f"Unsafe path detected in archive: {member.filename}")

            if os.path.exists(target_path) and not overwrite:
                if verbose:
                    print(f"[SKIP] Exists (no overwrite): {member.filename}")
                continue

            if verbose:
                print(f"[EXTRACT] {member.filename}")
            zf.extract(member, output_dir)

    print(f"[OK] Extracted ZIP archive to: {output_dir}")


# ----------------------------------------------------------------------
# CLI / argument parsing
# ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{TOOL_NAME}\n\n"
                    "Create and extract ZIP archives with optional exclusions and password protection.\n"
                    "Designed as a single-file, confidential-friendly utility.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "-zip",
        action="store_true",
        help="Create a ZIP archive from a directory.",
    )
    mode_group.add_argument(
        "-unzip",
        action="store_true",
        help="Extract a ZIP archive to a directory.",
    )

    parser.add_argument(
        "-d",
        "--directory",
        metavar="DIR",
        help="Directory to zip (default: current directory when using -zip).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Output file (for -zip) or output directory (for -unzip).",
    )
    parser.add_argument(
        "-i",
        "--input",
        metavar="ZIPFILE",
        help="Input ZIP file (required for -unzip).",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        metavar="PATTERN",
        nargs="*",
        help="File patterns to exclude when zipping (e.g. '*.log' 'node_modules/*').",
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="PASSWORD",
        help="Password for ZIP (ZipCrypto; light protection, not strong encryption).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="When extracting, overwrite existing files without prompting.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show tool version and exit.",
    )

    return parser


def print_version() -> None:
    print_branding()
    print(f"Version: {TOOL_VERSION}")
    print("Vendor: Astral Haven Development\n")


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print_version()
        return

    print_branding()

    try:
        if args.zip:
            directory = args.directory or os.getcwd()
            output = args.output or os.path.join(os.getcwd(), "archive.zip")
            zip_directory(
                directory=directory,
                output_file=output,
                exclude=args.exclude,
                password=args.password,
                verbose=args.verbose,
            )

        elif args.unzip:
            if not args.input:
                parser.error("The -i/--input argument is required when using -unzip.")

            output_dir = args.output or os.path.join(os.getcwd(), "unzipped")
            unzip_file(
                input_file=args.input,
                output_dir=output_dir,
                password=args.password,
                verbose=args.verbose,
                overwrite=args.overwrite,
            )

    except (FileNotFoundError, PermissionError, zipfile.BadZipFile) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        # zipfile may raise RuntimeError for bad passwords, etc.
        print(f"[ERROR] Runtime error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[ABORTED] Operation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()