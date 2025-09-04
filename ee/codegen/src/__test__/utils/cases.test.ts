import {
  createPythonClassName,
  toKebabCase,
  toPythonSafeSnakeCase,
  toValidPythonIdentifier,
} from "src/utils/casing";

describe("Casing utility functions", () => {
  describe("toKebabCase", () => {
    const testCases = [
      { input: "hello world", expected: "hello-world" },
      { input: "HelloWorld", expected: "hello-world" },
      { input: "hello_world", expected: "hello-world" },
      { input: "Hello World_Example-123", expected: "hello-world-example-123" },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected'",
      ({ input, expected }) => {
        expect(toKebabCase(input)).toBe(expected);
      }
    );
  });

  describe("createPythonClassName", () => {
    const testCases: [string, string][] = [
      // Basic cases
      ["hello world", "HelloWorld"],
      ["simpleTestCase", "SimpleTestCase"],
      // Special characters
      ["hello-world", "HelloWorld"],
      ["$special#characters%", "SpecialCharacters"],
      // Numbers
      ["123 invalid class name", "Class123InvalidClassName"],
      ["mixed 123 cases", "Mixed123Cases"],
      // Underscores
      ["_leading_underscores_", "LeadingUnderscores"],
      ["trailing_underscores_", "TrailingUnderscores"],
      ["_123numbers_starting", "Class123NumbersStarting"],
      // Empty and invalid input
      ["", "Class"],
      ["123", "Class123"],
      ["_123_", "Class123"],
      // Complex cases
      ["complex mix_of-DifferentCases", "ComplexMixOfDifferentCases"],
      ["ALLCAPS input", "ALLCAPSInput"], // Preserve ALLCAPS as requested
      ["PascalCaseAlready", "PascalCaseAlready"],
    ] as const;

    it.each<[string, string]>(testCases)(
      "should convert %s' to %s'",
      (input, expected) => {
        expect(createPythonClassName(input)).toBe(expected);
      }
    );
  });

  describe("toPythonSafeSnakeCase", () => {
    const testCases = [
      {
        input: "hello-world",
        safetyPrefix: undefined,
        expected: "hello_world",
      },
      { input: "HelloWorld", safetyPrefix: undefined, expected: "hello_world" },
      {
        input: "hello world",
        safetyPrefix: undefined,
        expected: "hello_world",
      },
      {
        input: "Hello-World_Example 123",
        safetyPrefix: undefined,
        expected: "hello_world_example_123",
      },
      {
        input: "$hello*World",
        safetyPrefix: undefined,
        expected: "hello_world",
      },
      {
        input: "$1hello*World",
        safetyPrefix: undefined,
        expected: "_1hello_world",
      },
      {
        input: "$1hello*World",
        safetyPrefix: "module",
        expected: "module_1hello_world",
      },
      {
        input: "$1hello*World",
        safetyPrefix: "attr",
        expected: "attr_1hello_world",
      },
      {
        input: "$1hello*World",
        safetyPrefix: "attr_",
        expected: "attr_1hello_world",
      },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected'",
      ({ input, safetyPrefix, expected }) => {
        expect(toPythonSafeSnakeCase(input, safetyPrefix)).toBe(expected);
      }
    );
  });

  describe("toValidPythonIdentifier", () => {
    const testCases = [
      // Core cases - valid identifiers preserved (APO-1372 fix)
      {
        input: "getCWD",
        safetyPrefix: undefined,
        expected: "getCWD",
        description: "camelCase should be preserved",
      },
      {
        input: "parseJSON",
        safetyPrefix: undefined,
        expected: "parseJSON",
        description: "mixed case should be preserved",
      },
      {
        input: "normalFunction",
        safetyPrefix: undefined,
        expected: "normalFunction",
        description: "standard camelCase should be preserved",
      },
      {
        input: "foo_bar",
        safetyPrefix: undefined,
        expected: "foo_bar",
        description: "snake_case should be preserved",
      },
      // Invalid identifiers converted to safe versions
      {
        input: "123invalid",
        safetyPrefix: undefined,
        expected: "_123invalid",
        description: "numbers at start get underscore prefix",
      },
      {
        input: "123invalid",
        safetyPrefix: "output",
        expected: "output_123invalid",
        description: "numbers at start get custom prefix",
      },
      {
        input: "special-chars!",
        safetyPrefix: undefined,
        expected: "special_chars",
        description: "special chars converted to snake_case",
      },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected' - $description",
      ({ input, safetyPrefix, expected }) => {
        expect(toValidPythonIdentifier(input, safetyPrefix)).toBe(expected);
      }
    );
  });
});
