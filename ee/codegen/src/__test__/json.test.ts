import { Writer } from "src/generators/extensions/writer";
import { Json } from "src/generators/json";

describe("Json", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  describe("write", () => {
    it("should handle null values", async () => {
      const json = new Json(null);
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle undefined values", async () => {
      const json = new Json(undefined);
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle strings", async () => {
      const json = new Json("test string");
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle integers", async () => {
      const json = new Json(42);
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle floats", async () => {
      const json = new Json(3.14);
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle booleans", async () => {
      const jsonTrue = new Json(true);
      jsonTrue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();

      writer = new Writer();
      const jsonFalse = new Json(false);
      jsonFalse.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle arrays", async () => {
      const json = new Json([1, "test", true]);
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle objects", async () => {
      const json = new Json({ key: "value", num: 123 });
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle nested structures", async () => {
      const json = new Json({
        array: [1, 2, 3],
        nested: { a: 1, b: "test" },
        null: null,
      });
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle complex nested structures", async () => {
      const json = new Json({
        id: "complex-123",
        metadata: {
          created: "2024-01-01",
          modified: "2024-01-02",
          tags: ["important", "test", "complex"],
        },
        data: {
          users: [
            {
              id: 1,
              name: "John Doe",
              settings: {
                preferences: {
                  theme: "dark",
                  notifications: true,
                },
                permissions: ["read", "write"],
              },
              scores: [98.5, 87.2, 92.0],
            },
            {
              id: 2,
              name: "Jane Smith",
              settings: {
                preferences: {
                  theme: "light",
                  notifications: false,
                },
                permissions: ["read"],
              },
              scores: [95.0, 88.5, 91.2],
            },
          ],
          statistics: {
            total: 2,
            active: true,
            averageScore: 92.07,
            metadata: {
              lastUpdated: "2024-01-02",
              source: "system",
              flags: [null, true, false],
            },
          },
        },
      });
      json.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should throw error for non-JSON-serializable values", () => {
      expect(() => new Json(() => {})).toThrow(
        "Unsupported JSON value type: function"
      );
      expect(() => new Json(Symbol())).toThrow(
        "Unsupported JSON value type: symbol"
      );
    });
  });
});
