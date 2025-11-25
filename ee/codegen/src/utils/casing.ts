const PYTHON_KEYWORDS = new Set([
  "False",
  "None",
  "True",
  "__peg_parser__",
  "and",
  "as",
  "assert",
  "async",
  "await",
  "break",
  "class",
  "continue",
  "def",
  "del",
  "elif",
  "else",
  "except",
  "finally",
  "for",
  "from",
  "global",
  "if",
  "import",
  "in",
  "is",
  "lambda",
  "nonlocal",
  "not",
  "or",
  "pass",
  "raise",
  "return",
  "try",
  "while",
  "with",
  "yield",
]);

export function escapePythonKeyword(name: string): string {
  return PYTHON_KEYWORDS.has(name) ? `${name}_` : name;
}

export function toKebabCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, "$1-$2") // Insert hyphen between lower and upper case
    .replace(/[\s_]+/g, "-") // Replace spaces and underscores with hyphens
    .replace(/[^a-zA-Z0-9]+/g, "-") // Replace consecutive non-alphanumeric characters with a single hyphen
    .replace(/^-+|-+$/g, "") // Remove leading and trailing hyphens
    .toLowerCase(); // Convert to lowercase
}

/**
 * Converts a string to a valid Python class name.
 * @param input the input string to convert to a Python class name
 * @param options the options for the conversion
 * @param options.force whether to force the PascalCase conversion no matter what the input is
 * @returns the converted Python class name
 */
export function createPythonClassName(
  input: string,
  options: { force?: boolean } = {}
): string {
  // Handle empty input
  if (!input) {
    return "Class";
  }

  // Clean up the input string
  let cleanedInput = input
    .replace(/[^a-zA-Z0-9\s_-]/g, " ") // Replace special characters with spaces
    .replace(/[-_\s]+/g, " ") // Replace hyphens, underscores and multiple spaces with single space
    .trim(); // Remove leading/trailing spaces

  // Handle numeric-only or empty string after cleanup
  if (!cleanedInput || /^\d+$/.test(cleanedInput)) {
    return "Class" + (cleanedInput || "");
  }

  // Handle strings starting with numbers
  if (/^\d/.test(cleanedInput)) {
    cleanedInput = "Class" + cleanedInput;
  }

  // Split into words and handle special cases
  const splitRegex = options?.force
    ? /(?<=[a-z])(?=[A-Z])|[-_\s]+/
    : /(?=[A-Z])|[-_\s]+/;
  const words = cleanedInput
    .split(splitRegex)
    .filter((word) => word.length > 0)
    .map((word) => {
      // Fix any garbled text by splitting on number boundaries
      return word
        .split(/(?<=\d)(?=[a-zA-Z])|(?<=[a-zA-Z])(?=\d)/)
        .filter((w) => w.length > 0);
    })
    .flat();

  // Process each word
  return words
    .map((word, index) => {
      // If it's the first word and starts with a number, prepend "Class"
      if (index === 0 && /^\d/.test(word)) {
        return (
          "Class" + word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        );
      }
      // Preserve words that are all uppercase and longer than one character
      if (
        word.length > 1 &&
        word === word.toUpperCase() &&
        !/^\d+$/.test(word) &&
        !options?.force
      ) {
        return word;
      }
      // Capitalize first letter, lowercase rest
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join("");
}

export function toPythonSafeSnakeCase(
  str: string,
  safetyPrefix: string = "_"
): string {
  // Strip special characters from start of string
  const cleanedStr = str.replace(/^[^a-zA-Z0-9_]+/, "");

  // Check if cleaned string starts with a number or an underscore
  const startsWithUnsafe = /^[\d_]/.test(cleanedStr);

  const snakeCase = cleanedStr
    .replace(/([a-z])([A-Z])/g, "$1_$2") // Insert underscore between lower and upper case
    .replace(/[^a-zA-Z0-9]+/g, "_") // Replace any non-alphanumeric characters with underscore
    .replace(/^_+|_+$/g, "") // Remove any leading/trailing underscores
    .toLowerCase(); // Convert to lowercase

  // Add underscore prefix if cleaned string started with unsafe chars
  const cleanedSafetyPrefix =
    safetyPrefix === "_"
      ? "_"
      : `${safetyPrefix}${safetyPrefix.endsWith("_") ? "" : "_"}`;
  return startsWithUnsafe ? cleanedSafetyPrefix + snakeCase : snakeCase;
}

export function toValidPythonIdentifier(
  str: string,
  safetyPrefix: string = "_"
): string {
  // Strip special characters from start of string
  const cleanedStr = str.replace(/^[^a-zA-Z0-9_]+/, "");

  // Check if cleaned string starts with a number or an underscore
  const startsWithUnsafe = /^[\d_]/.test(cleanedStr);

  // Check if the string is already a valid Python identifier (preserve case)
  const isValidPythonIdentifier = /^[a-zA-Z][a-zA-Z0-9]*$/.test(cleanedStr);

  if (isValidPythonIdentifier && !startsWithUnsafe) {
    return escapePythonKeyword(cleanedStr);
  }

  return escapePythonKeyword(toPythonSafeSnakeCase(str, safetyPrefix));
}

export function removeEscapeCharacters(str: string): string {
  return str.replace(/\\"/g, '"');
}

/**
 * Converts a PascalCase string to Title Case with spaces.
 * This mirrors the Python implementation in vellum.workflows.utils.names.pascal_to_title_case
 *
 * Examples:
 * - "MyCustomNode" -> "My Custom Node"
 * - "APINode" -> "API Node"
 * - "SimpleAPINode" -> "Simple API Node"
 *
 * @param pascalStr the PascalCase string to convert
 * @returns the Title Case string with spaces
 */
export function pascalToTitleCase(pascalStr: string): string {
  // Insert spaces between:
  // 1. A lowercase letter followed by an uppercase letter (e.g., "myNode" -> "my Node")
  // 2. An uppercase letter followed by an uppercase letter and then a lowercase letter (e.g., "APINode" -> "API Node")
  const titleCaseStr = pascalStr.replace(
    /(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])/g,
    " "
  );

  const words = titleCaseStr.split(/\s+/);
  const resultWords = words.map((word) => {
    // If the word is all uppercase, keep it as-is
    if (word === word.toUpperCase()) {
      return word;
    }
    // Otherwise, capitalize the first letter and lowercase the rest
    return word.charAt(0).toUpperCase() + word.slice(1);
  });

  return resultWords.join(" ");
}
