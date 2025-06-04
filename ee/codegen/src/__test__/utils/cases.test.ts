import {
  createPythonClassName,
  toKebabCase,
  toPythonSafeSnakeCase,
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
      {
        input: "fooBAR",
        safetyPrefix: undefined,
        expected: "foo_bar",
      },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected'",
      ({ input, safetyPrefix, expected }) => {
        expect(toPythonSafeSnakeCase(input, safetyPrefix)).toBe(expected);
      }
    );
  });
});
