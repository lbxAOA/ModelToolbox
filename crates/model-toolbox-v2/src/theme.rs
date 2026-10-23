use gpui_kit::component::{Theme, ThemeRegistry};
use gpui_kit::*;

const THEMES: &str = include_str!("../themes/model-toolbox.json");

pub fn init(cx: &mut App) {
	ThemeRegistry::global_mut(cx)
		.load_themes_from_str(THEMES)
		.expect("failed to load ModelToolbox theme");

	let (light, dark) = {
		let registry = ThemeRegistry::global(cx);
		(
			registry
				.themes()
				.get("ModelToolbox Light")
				.cloned()
				.expect("ModelToolbox Light theme"),
			registry
				.themes()
				.get("ModelToolbox Dark")
				.cloned()
				.expect("ModelToolbox Dark theme"),
		)
	};

	let theme = Theme::global_mut(cx);
	theme.light_theme = light;
	theme.dark_theme = dark;
	Theme::sync_system_appearance(None, cx);
}
