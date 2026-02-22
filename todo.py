import colorama

print(colorama.Fore.MAGENTA + """
▓▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓   ▓▓▓▓▓
  ▓▓   ▓▓   ▓▓ ▓▓   ▓▓ ▓▓   ▓▓
  ▓▓   ▓▓   ▓▓ ▓▓   ▓▓ ▓▓   ▓▓
  ▓▓   ▓▓   ▓▓ ▓▓   ▓▓ ▓▓   ▓▓
  ▓▓   ▓▓   ▓▓ ▓▓   ▓▓ ▓▓   ▓▓
  ▓▓    ▓▓▓▓▓  ▓▓▓▓▓▓   ▓▓▓▓▓
""" + colorama.Style.RESET_ALL)
print(colorama.Fore.MAGENTA + "These the features that need to be either added or fixed in the bot." + colorama.Style.RESET_ALL)
print(colorama.Fore.MAGENTA + "If you want to help, please read the CONTRIBUTING.md file in the official GitHub repository." + colorama.Style.RESET_ALL)
print(colorama.Fore.MAGENTA + "GitHub: https://github.com/developer51709/Niko" + colorama.Style.RESET_ALL)
print()
print("TODO:")
print("1. Add better-sqlite3 for economy storage persistence.")
print("2. Add support for other AI models (Mistral, Phi-3, etc).")
print("3. Do a full debugging of the bot.")
print("4. Expand the economy system.")