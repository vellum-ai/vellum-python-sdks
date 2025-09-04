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
      // Valid identifiers should be preserved (APO-1372 fix)
      {
        input: "fooBAR",
        safetyPrefix: undefined,
        expected: "fooBAR",
      },
      {
        input: "foo_bar",
        safetyPrefix: undefined,
        expected: "foo_bar",
      },
      {
        input: "getCWD",
        safetyPrefix: undefined,
        expected: "getCWD",
        description: "camelCase should be preserved"
      },
      {
        input: "parseJSON",
        safetyPrefix: undefined,
        expected: "parseJSON",
        description: "mixed case should be preserved"
      },
      {
        input: "XMLHttpRequest",
        safetyPrefix: undefined,
        expected: "XMLHttpRequest",
        description: "multiple caps should be preserved"
      },
      {
        input: "normalFunction",
        safetyPrefix: undefined,
        expected: "normalFunction",
        description: "standard camelCase should be preserved"
      },
      // Invalid identifiers should be converted to safe snake_case
      {
        input: "123invalid",
        safetyPrefix: "output",
        expected: "output_123invalid",
        description: "numbers at start should get prefix"
      },
      {
        input: "123invalid",
        safetyPrefix: undefined,
        expected: "_123invalid",
        description: "numbers at start should get default prefix"
      },
      {
        input: "special-chars!",
        safetyPrefix: undefined,
        expected: "special_chars",
        description: "special characters should be converted to snake_case"
      },
      {
        input: "_underscore_start",
        safetyPrefix: undefined,
        expected: "_underscore_start",
        description: "underscore at start should get prefix"
      },
      {
        input: "with spaces",
        safetyPrefix: undefined,
        expected: "with_spaces",
        description: "spaces should be converted to snake_case"
      },
      {
        input: "ALLCAPS_CONSTANT",
        safetyPrefix: undefined,
        expected: "allcaps_constant",
        description: "all caps with underscores converted to snake_case"
      },
      // Edge cases
      {
        input: "",
        safetyPrefix: undefined,
        expected: "",
        description: "empty string should remain empty"
      },
      {
        input: "a",
        safetyPrefix: undefined,
        expected: "a",
        description: "single character should be preserved"
      },
      {
        input: "A",
        safetyPrefix: undefined,
        expected: "A",
        description: "single uppercase character should be preserved"
      },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected' - $description",
      ({ input, safetyPrefix, expected }) => {
        expect(toValidPythonIdentifier(input, safetyPrefix)).toBe(expected);
      }
    );

    describe("APO-1372 specific regression tests", () => {
      it("should preserve camelCase function names that are valid Python identifiers", () => {
        const camelCaseFunctions = [
          "getCwd",
          "parseJson",
          "fetchData",
          "calculateTotal",
          "renderTemplate"
        ];

        camelCaseFunctions.forEach(functionName => {
          const result = toValidPythonIdentifier(functionName);
          expect(result).toBe(functionName);
        });
      });

      it("should handle complex camelCase names correctly", () => {
        const complexNames = [
          { input: "XMLHttpRequest", expected: "XMLHttpRequest" },
          { input: "HTMLParser", expected: "HTMLParser" },
          { input: "JSONEncoder", expected: "JSONEncoder" },
          { input: "URLBuilder", expected: "URLBuilder" }
        ];

        complexNames.forEach(({ input, expected }) => {
          expect(toValidPythonIdentifier(input)).toBe(expected);
        });
      });

      it("should convert unsafe identifiers to snake_case while preserving safe ones", () => {
        const mixedCases = [
          { input: "validFunction", expected: "validFunction" }, // Valid - preserve
          { input: "123Invalid", expected: "_123invalid" }, // Invalid - convert
          { input: "special-chars", expected: "special_chars" }, // Invalid - convert
          { input: "normalName", expected: "normalName" }, // Valid - preserve
        ];

        mixedCases.forEach(({ input, expected }) => {
          expect(toValidPythonIdentifier(input)).toBe(expected);
        });
      });
    });
  });
});
