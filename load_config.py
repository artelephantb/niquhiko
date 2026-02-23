import tomli

class Config:
	def load(self, config_file: str):
		with open(config_file, 'rb') as file:
			site_config = tomli.load(file)

		self.site_name = site_config['site_name']
		self.footnote = site_config['footnote']

		self.site_colors = site_config['site_colors']

		self.site_color_background = self.site_colors['background']
		self.site_color_background_accent = self.site_colors['background_accent']

		self.site_color_text = self.site_colors['text']
		self.site_color_text_light = self.site_colors['text_light']

		self.site_color_accent = self.site_colors['accent']
		self.site_color_accent_hover = self.site_colors['accent_hover']

		self.site_color_accent_text = self.site_colors['accent_text']

		self.site_color_code = self.site_colors['code']

		self.site_color_preformatted = self.site_colors['preformatted']

		self.site_color_disabled = self.site_colors['disabled']

		self.roles = site_config['roles']

		self.allowed_clean = site_config['allowed_clean']

		self.allowed_clean_html_tags = self.allowed_clean['html_tags']
		self.allowed_clean_html_attributes = self.allowed_clean['html_attributes']

		self.allowed_clean_letters = self.allowed_clean['letters']
		self.allowed_clean_characters = self.allowed_clean['characters']

		self.allowed_file_extensions = self.allowed_clean['allowed_file_extensions']

		self.link_badges_dict = site_config['link_badges']
		self.link_badges = []

		for badge_key in self.link_badges_dict.keys():
			self.link_badges.append(self.link_badges_dict[badge_key])
