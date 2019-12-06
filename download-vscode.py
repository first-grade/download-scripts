'''Downloader for Visual Studio Code for offline usage

Downloads the VSCode installation and extensions (as .vsix) for offline usage.
'''
from __future__ import print_function

import os
import re
import time
import shutil
from selenium import webdriver

import common

DOWNLOAD_SUBFOLDER = 'vscode'
DOWNLOAD_BASE_PATH = os.path.join(common.DOWNLOAD_PATH, DOWNLOAD_SUBFOLDER)
DOWNLOAD_INSTALLER_PATH = os.path.join(DOWNLOAD_BASE_PATH, 'vscode') + os.path.sep
DOWNLOAD_EXTENSIONS_PATH = os.path.join(DOWNLOAD_BASE_PATH, 'extensions') + os.path.sep

_EXTENSION_FILE_BASE_RE = r'^{name}.*\.vsix$'

_EXTENSIONS_BY_CATEGORIES = {
    'core' : {
        '2gua.rainbow-brackets',
        'alexdima.copy-relative-path',
        'bbenoist.togglehs',
        'formulahendry.auto-close-tag',
        'formulahendry.auto-rename-tag',
        'ionutvmi.path-autocomplete',
        'ms-vscode.wordcount',
        'oderwat.indent-rainbow',
        'slevesque.vscode-hexdump',
        'slevesque.vscode-multiclip',
        'wmaurer.change-case',
    },
    'utils' : {
        'alefragnani.bookmarks',
        'alefragnani.numbered-bookmarks',
        'alefragnani.project-manager',
        'anseki.vscode-color', # problematic? need to `npm install` before launch
        'christian-kohler.path-intellisense', # path autocomplete might be better
        'cschlosser.doxdocgen',
        'donjayamanne.githistory',
        'eamodio.gitlens',
        'EditorConfig.EditorConfig',
        'esbenp.prettier-vscode',
        'fabiospampinato.vscode-todo-plus',
        'felipecaputo.git-project-manager',
        'formulahendry.code-runner',
        'formulahendry.terminal',
        'hackerfinn.vscode-todo-renewed',
        'hbenl.vscode-firefox-debug',
        'helixquar.asciidecorator',
        'hookyqr.beautify',
        'jakob101.relativepath',
        'jebbs.plantuml', # problematic! look at marketplace for installations
        'joelday.docthis',
        'juliencroain.markdown-viewer',
        'juliencroain.private-extension-manager',
        'minhthai.vscode-todo-parser',
        'msjsdiag.debugger-for-chrome',
        'msjsdiag.debugger-for-edge',
        'naumovs.color-highlight',
        'shakram02.bash-beautify',
        'tomoki1207.pdf',
        'tushortz.pygame-snippets',
        'tyriar.lorem-ipsum',
        'waderyan.gitblame',
        'yzane.markdown-pdf', # problematic! needs puppeteer extension for chrome/chromium
        'mhutchie.git-graph',
        'Tyriar.sort-lines',
    },
    'language' : {
        'abusaidm.html-snippets',
        'ajshort.include-autocomplete',
        'christian-kohler.npm-intellisense', # problematic? probably needs npm?
        'davidanson.vscode-markdownlint',
        'dbaeumer.vscode-eslint', # problematic? needs `npm install -g eslint`
        'dbankier.vscode-instant-markdown',
        'devcat.lua-debug',
        'dotjoshjohnson.xml',
        'ecmel.vscode-html-css',
        'eg2.vscode-npm-script',
        'felixfbecker.php-intellisense',
        'goessner.mdmath',
        'hars.CppSnippets',
        'hvyindustries.crane',
        'jomiller.rtags-client',
        'magicstack.magicpython',
        'mitaki28.vscode-clang',
        'ms-python.python',
        'ms-vscode.cpptools', # problematic! - needs intellisense (find from marketplace page)
        'ms-vscode.csharp', # problematic! needs OmniSharp (find from marketplace page)
        'ms-vscode.powershell',
        'peterjausovec.vscode-docker',
        'redhat.java',
        'redhat.vscode-yaml',
        'satoren.lualint',
        'sidthesloth.html5-boilerplate',
        'tobiah.comment-snippets',
        'tushortz.python-extended-snippets',
        'twxs.cmake',
        'vector-of-bool.cmake-tools',
        'wcwhitehead.bootstrap-3-snippets',
        'webfreak.debug',
        'xabikos.javascriptsnippets',
        'xabikos.reactsnippets',
        'zignd.html-css-class-completion',
    },
    'spell checkers' : {
        'ban.spellright',
        'streetsidesoftware.code-spell-checker',
        'streetsidesoftware.code-spell-checker-medical-terms',
        'swyphcosmo.spellchecker',
    },
    'keymaps' : {
        'k--kato.intellij-idea-keybindings',
        'ms-vscode.atom-keybindings',
        'ms-vscode.notepadplusplus-keybindings',
        'ms-vscode.sublime-keybindings',
        'ms-vscode.vs-keybindings',
        'vscodevim.vim',
    },
    'themes' : {
        'akamud.vscode-theme-onedark',
        'akamud.vscode-theme-onelight',
        'azemoh.theme-onedark',
        'be5invis.vscode-icontheme-nomo-dark',
        'carlos-dev-pereira.nightcode',
        'davidbabel.vscode-simpler-icons',
        'daylerees.rainglow',
        'dracula-theme.theme-dracula',
        'dunstontc.dark-plus-syntax',
        'emmanuelbeziat.vscode-great-icons',
        'equinusocio.vsc-material-theme',
        'file-icons.file-icons',
        'freebroccolo.theme-atom-one-dark',
        'jamesmaj.easy-icons',
        'jez9999.vsclassic-icon-theme',
        'johnpapa.winteriscoming',
        'jordang.vs-one-dark-theme',
        'jprestidge.theme-material-theme',
        'jtlowe.vscode-icon-theme',
        'karyfoundation.theme-karyfoundation-themes',
        'laurenttreguier.vscode-simple-icons',
        'monokai.theme-monokai-pro-vscode',
        'ms-vscode.Theme-1337',
        'ms-vscode.theme-markdownkit',
        'ms-vscode.theme-materialkit',
        'pkief.material-icon-theme',
        'qinjia.seti-icons',
        'robertohuertasm.vscode-icons',
        'Scatolina.theme-monokaiextended',
        'sdras.night-owl',
        'sldobri.bunker',
        'smlombardi.darcula-extended',
        'stepanog.cage-icons',
        'syncap.sc-themes',
        'tushortz.theme-wildlife',
        'vangware.dark-plus-material',
        'whizkydee.material-palenight-theme',
        'zhuangtongfa.material-theme',
        'max-SS.cyberpunk',
    },
    'miscellaneous' : {
        'hoovercj.vscode-power-mode'
    },
    'experimental utils' : {
        'Atlassian.atlascode',
        'gioboa.jira-plugin',
        'bb-spectacle.bb-spectacle',
        'RamiroBerrelleza.bitbucket-pull-requests',
        'pstreule.codebucket',
        'denco.confluence-markup',
        'letmaik.git-tree-compare',
        'mkloubert.vscode-kanban',
        'axosoft.gitkraken-glo',
        'secanis.jenkinsfile-support',
        'marlon407.code-groovy',
        'rogalmic.bash-debug',
    }
}

_UNIQUE_EXTENSIONS = {
    'ms-vscode.cpptools' : {
        'run_default' : False,
    }
}

def extension_url(extension_name):
    '''
    Creates the extension's marketplace URL.

    @param extension_name   The extension's name as refered by vscode in the format: '{author}.{name}'.

    @return str
    '''
    return 'https://marketplace.visualstudio.com/items?itemName={}'.format(extension_name)

def open_maketplace_page(extension_name):
    '''
    Opens the Visual Studio Code Maketplace page for the given extension.

    @param extension_name   The extension's name as refered by vscode in the format: '{author}.{name}'.
    '''
    os.system('"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" --incognito {}'.format(extension_url(extension_name)))

def all_extensions():
    '''
    Returns an iterable object that iterates through all listed extensions.

    @return An iterable object
    '''
    return (ext for category in _EXTENSIONS_BY_CATEGORIES
                for ext in _EXTENSIONS_BY_CATEGORIES[category])

def get_category(extension_name):
    '''
    TODO: document
    '''
    for category in _EXTENSIONS_BY_CATEGORIES:
        if extension_name in _EXTENSIONS_BY_CATEGORIES[category]:
            return category
    return 'unknown'

def to_dirname(category):
    '''
    TODO: document
    '''
    return ''.join(word.capitalize() for word in category.split())

def _get_download_button(driver):
    for i in xrange(1000): # 1000 tries
        for element in driver.find_elements_by_tag_name('button'):
            if element.text == 'Download Extension':
                return element

def _check_for_file(filename, download_path):
    if isinstance(filename, str):
        match = lambda x: filename == x
    else:
        match = filename.match

    return any(match(existing_file) for existing_file in os.listdir(download_path))

def _wait_for_file(filename, download_path):
    while not _check_for_file(filename, download_path):
        time.sleep(1)

class _Downloader():
    '''
    TODO: document
    '''
    def __init__(self, download_path=DOWNLOAD_BASE_PATH, extensions_path=DOWNLOAD_EXTENSIONS_PATH, use_categories=True):
        self._download_path = download_path
        self._ext_path = extensions_path
        self._use_categories = use_categories
        self._exts_in_progress = []

        options = webdriver.ChromeOptions()

        preferences = { "download.default_directory" : self._download_path }
        options.add_experimental_option("prefs", preferences)
        options.add_argument("--incognito")

        self._driver = webdriver.Chrome(chrome_options=options)

    def download_extension(self, extension_name):
        self._driver.get(extension_url(extension_name))
        assert self._driver.title.endswith(' - Visual Studio Marketplace')

        _get_download_button(self._driver).click()

        self._exts_in_progress.append(extension_name)

    def download_extensions(self, extensions):
        for ext in extensions:
            self.download_extension(ext)

    @staticmethod
    def _get_extension_re(extension_name):
        return re.compile(_EXTENSION_FILE_BASE_RE.format(name=extension_name))

    def _get_extension_filename(self, extension_name):
        extension_file_re = self._get_extension_re(extension_name)
        for ext_file in os.listdir(self._download_path):
            if extension_file_re.match(ext_file):
                return ext_file

    def _wait_for_extension(self, extension_name):
        _wait_for_file(self._get_extension_re(extension_name), self._download_path)

        if self._use_categories:
            dst_path = os.path.join(self._ext_path, to_dirname(get_category(extension_name)))
        else:
            dst_path = self._ext_path

        common.create_downloads(dst_path, clean=False)

        filename = self._get_extension_filename(extension_name)
        src = os.path.join(self._download_path, filename)
        dst = os.path.join(dst_path, filename)
        shutil.move(src, dst)

    def _wait_for_all_extensions(self):
        for ext in self._exts_in_progress:
            self._wait_for_extension(ext)

    def _wait_for_downloads(self):
        self._wait_for_all_extensions()

    def _dispose(self):
        if self._driver is None:
            return

        self._wait_for_downloads()
        self._driver.quit()
        self._driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._dispose()

    def __del__(self):
        self._dispose()

def download_extension(extension_name):
    '''
    TODO: document
    '''
    print("Downloading: ", extension_name)

    with _Downloader() as downloader:
        downloader.download_extension(extension_name)

def download_extensions(extensions):
    '''
    TODO: document
    '''
    print("Downloading: ", ', '.join(extensions))

    with _Downloader() as downloader:
        downloader.download_extensions(extensions)

if __name__ == '__main__':
    common.create_downloads(DOWNLOAD_BASE_PATH)
    common.create_downloads(DOWNLOAD_INSTALLER_PATH)
    common.create_downloads(DOWNLOAD_EXTENSIONS_PATH)

    download_extensions(all_extensions())
