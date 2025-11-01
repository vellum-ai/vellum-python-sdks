import {
  createPythonClassName,
  escapePythonKeyword,
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
      ["SLACK_MESSAGE_TRIGGER", "SLACKMESSAGETRIGGER"],
      ["APISuccessOutput", "APISuccessOutput"],
    ] as const;

    it.each<[string, string]>(testCases)(
      "should convert %s' to %s'",
      (input, expected) => {
        expect(createPythonClassName(input)).toBe(expected);
      }
    );
  });

  describe("createPythonClassName force:true", () => {
    const testCases: [string, string][] = [
      ["SLACK_MESSAGE_TRIGGER", "SlackMessageTrigger"],
    ] as const;

    it.each<[string, string]>(testCases)(
      "should convert %s' to %s'",
      (input, expected) => {
        expect(createPythonClassName(input, { force: true })).toBe(expected);
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

  describe("escapePythonKeyword", () => {
    const testCases = [
      { input: "class", expected: "class_" },
      { input: "import", expected: "import_" },
      { input: "from", expected: "from_" },
      { input: "def", expected: "def_" },
      { input: "if", expected: "if_" },
      { input: "for", expected: "for_" },
      { input: "while", expected: "while_" },
      { input: "return", expected: "return_" },
      { input: "True", expected: "True_" },
      { input: "False", expected: "False_" },
      { input: "None", expected: "None_" },
      { input: "normal_name", expected: "normal_name" },
      { input: "myVariable", expected: "myVariable" },
    ];

    it.each(testCases)(
      "should escape '$input' to '$expected'",
      ({ input, expected }) => {
        expect(escapePythonKeyword(input)).toBe(expected);
      }
    );
  });

  describe("toValidPythonIdentifier", () => {
    const testCases = [
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
        input: "123invalid",
        safetyPrefix: "output",
        expected: "output_123invalid",
      },
      {
        input: "class",
        safetyPrefix: undefined,
        expected: "class_",
      },
      {
        input: "import",
        safetyPrefix: undefined,
        expected: "import_",
      },
      {
        input: "for",
        safetyPrefix: "input",
        expected: "for_",
      },
      {
        input: "normal-name",
        safetyPrefix: undefined,
        expected: "normal_name",
      },
    ];

    it.each(testCases)(
      "should convert '$input' to '$expected'",
      ({ input, safetyPrefix, expected }) => {
        expect(toValidPythonIdentifier(input, safetyPrefix)).toBe(expected);
      }
    );
  });
});
