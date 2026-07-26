from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from modelingest.builder import BuildConfig, KnowledgeBaseBuilder


class BuilderPathTests(unittest.TestCase):
    def test_fetch_local_content_excludes_nested_output_and_temp(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "source"
            output = source / "output"
            temp_dir = source / "custom-temp"
            source.mkdir()
            output.mkdir()
            temp_dir.mkdir()
            (source / "input.md").write_text("source", encoding="utf-8")
            (output / "old.md").write_text("output", encoding="utf-8")
            (temp_dir / "old.md").write_text("temp", encoding="utf-8")

            config = BuildConfig(
                source=str(source),
                output=output,
                temp_dir=temp_dir,
                keep_temp=True,
            )
            builder = KnowledgeBaseBuilder(config)
            builder._prepare_directories()

            raw_dir = builder._fetch_content()
            copied_files = sorted(
                path.relative_to(raw_dir) for path in raw_dir.rglob("*") if path.is_file()
            )

            self.assertEqual(copied_files, [Path("input.md")])


if __name__ == "__main__":
    unittest.main()