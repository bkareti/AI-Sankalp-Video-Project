import unittest

from ai_sankalp.schema_validation import SchemaError, SchemaIssue, validate


def messages(instance, schema):
    return [str(issue) for issue in validate(instance, schema)]


class KeywordTests(unittest.TestCase):
    def test_type_names_and_bool_is_not_a_number(self):
        self.assertEqual([], messages(3, {"type": "integer"}))
        self.assertEqual([], messages(3.5, {"type": "number"}))
        self.assertEqual(["(root): must be of type number"], messages(True, {"type": "number"}))
        self.assertEqual(["(root): must be of type integer"], messages(True, {"type": "integer"}))
        self.assertEqual([], messages(None, {"type": ["string", "null"]}))
        self.assertEqual(["(root): must be of type string or null"], messages(1, {"type": ["string", "null"]}))

    def test_string_constraints(self):
        schema = {"type": "string", "minLength": 2, "maxLength": 3, "pattern": "^[a-z]+$"}
        self.assertEqual([], messages("ab", schema))
        self.assertIn("(root): must have at least 2 character(s)", messages("a", schema))
        self.assertIn("(root): must have at most 3 character(s)", messages("abcd", schema))
        self.assertTrue(any("does not match" in item for item in messages("A1", schema)))

    def test_numeric_bounds_enum_and_const(self):
        self.assertEqual(["(root): must be >= 0.5"], messages(0.1, {"minimum": 0.5}))
        self.assertEqual(["(root): must be <= 2"], messages(3, {"maximum": 2}))
        self.assertEqual(['(root): must be one of: "a", "b"'], messages("c", {"enum": ["a", "b"]}))
        self.assertEqual(['(root): must equal "x"'], messages("y", {"const": "x"}))

    def test_object_and_array_paths(self):
        schema = {
            "type": "object",
            "required": ["sections"],
            "properties": {
                "sections": {
                    "type": "array", "minItems": 1, "maxItems": 2,
                    "items": {"type": "object", "required": ["bullets"],
                              "properties": {"bullets": {"type": "array", "items": {"type": "string"}}}},
                },
            },
        }
        self.assertEqual(["sections: is required"], messages({}, schema))
        self.assertEqual(
            ["sections[1].bullets[0]: must be of type string"],
            messages({"sections": [{"bullets": []}, {"bullets": [3]}]}, schema),
        )
        self.assertEqual(["sections: must have at most 2 item(s)"],
                         messages({"sections": [{"bullets": []}] * 3}, schema))

    def test_additional_properties(self):
        schema = {"type": "object", "properties": {"a": {}}, "additionalProperties": {"type": "string"}}
        self.assertEqual(["b: must be of type string"], messages({"a": 1, "b": 2}, schema))
        self.assertEqual(["b: is not allowed"], messages({"b": 1}, {"additionalProperties": False}))

    def test_combinators(self):
        one_of = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual([], messages("x", one_of))
        self.assertTrue(messages(1.5, one_of))
        overlapping = {"oneOf": [{"type": "number"}, {"type": "integer"}]}
        self.assertEqual(["(root): matches more than one allowed form"], messages(1, overlapping))
        any_of = {"anyOf": [{"required": ["title"]}, {"required": ["lesson_title"]}]}
        self.assertEqual([], messages({"lesson_title": "x"}, any_of))
        self.assertEqual(["title: is required"], messages({}, any_of))
        all_of = {"allOf": [{"required": ["a"]}, {"required": ["b"]}]}
        self.assertEqual(["a: is required", "b: is required"], messages({}, all_of))

    def test_local_ref(self):
        schema = {"$defs": {"name": {"type": "string"}}, "properties": {"n": {"$ref": "#/$defs/name"}}}
        self.assertEqual(["n: must be of type string"], messages({"n": 1}, schema))

    def test_unknown_keyword_raises(self):
        with self.assertRaises(SchemaError):
            validate({}, {"patternProperties": {}})
        with self.assertRaises(SchemaError):
            validate({}, {"$ref": "other.json#/x"})

    def test_issue_str(self):
        self.assertEqual("a.b: bad", str(SchemaIssue("a.b", "bad")))


@unittest.skipUnless(__import__("importlib").util.find_spec("jsonschema"), "jsonschema not installed")
class ReferenceValidatorTests(unittest.TestCase):
    def test_matches_reference_jsonschema(self):
        import json
        from pathlib import Path

        import jsonschema

        from ai_sankalp.schema_validation import load_schema

        root = Path(__file__).resolve().parents[1]
        schema = load_schema("lesson.schema.json")
        for path in sorted(root.glob("examples/*.json")) + sorted(root.glob("examples/*/config.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([], validate(data, schema))
            jsonschema.validate(data, schema)


if __name__ == "__main__":
    unittest.main()
