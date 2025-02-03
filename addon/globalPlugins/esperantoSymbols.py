import os
import characterProcessing
from characterProcessing import SpeechSymbols
import config
import globalPluginHandler
import globalVars
from logHandler import log

old_getSpeechSymbolsForLocale = characterProcessing._getSpeechSymbolsForLocale
locale_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'locale'))

def _getSpeechSymbolsForLocale(locale):
	if locale != 'eo':
		return old_getSpeechSymbolsForLocale(locale)
	builtin = SpeechSymbols()
	if config.conf['speech']['includeCLDR']:
		# Try to load CLDR data when processing is on.
		# Load the data before loading other symbols,
		# in order to allow translators to override them.
		try:
			builtin.load(os.path.join(locale_path, locale, "cldr.dic"),
				allowComplexSymbols=False)
		except IOError:
			log.debugWarning("No CLDR data for locale %s" % locale)
	try:
		builtin.load(os.path.join(locale_path, locale, "symbols.dic"))
	except IOError:
		_noSymbolLocalesCache.add(locale)
		raise LookupError("No symbol information for locale %s" % locale)
	user = SpeechSymbols()
	try:
		# Don't allow users to specify complex symbols
		# because an error will cause the whole processor to fail.
		user.load(os.path.join(globalVars.appArgs.configPath, "symbols-%s.dic" % locale),
			allowComplexSymbols=False)
	except IOError:
		# An empty user SpeechSymbols is okay.
		pass
	return builtin, user

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		characterProcessing._getSpeechSymbolsForLocale = _getSpeechSymbolsForLocale
		characterProcessing._localeSpeechSymbolProcessors._localeDataFactory.localeSymbols._localeDataFactory = _getSpeechSymbolsForLocale

	def terminate(self):
		characterProcessing._getSpeechSymbolsForLocale = old_getSpeechSymbolsForLocale
		characterProcessing._localeSpeechSymbolProcessors._localeDataFactory.localeSymbols._localeDataFactory = old_getSpeechSymbolsForLocale
