'''Downloader for Visual Studio Code for offline usage

Downloads the VSCode installation and extensions (as .vsix) for offline usage.
'''
from __future__ import print_function

import os
import re
import time
import shutil
import itertools
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
        'firefox-devtools.vscode-firefox-debug',
        'formulahendry.code-runner',
        'formulahendry.terminal',
        'hackerfinn.vscode-todo-renewed',
        'helixquar.asciidecorator',
        'hookyqr.beautify',
        'jakob101.relativepath',
        'jebbs.plantuml', # problematic! look at marketplace for installations || hope graphiz will work
        'joelday.docthis',
        'juliencroain.markdown-viewer',
        'mhutchie.git-graph',
        'minhthai.vscode-todo-parser',
        'mkloubert.vscode-kanban',
        'msjsdiag.debugger-for-chrome',
        'msjsdiag.debugger-for-edge',
        'naumovs.color-highlight',
        'shakram02.bash-beautify',
        'tomoki1207.pdf',
        'tushortz.pygame-snippets',
        'tyriar.lorem-ipsum',
        'Tyriar.sort-lines',
        'waderyan.gitblame',
        'yzane.markdown-pdf', # needs puppeteer extension for chrome/chromium
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
        'jomiller.rtags-client',
        'magicstack.magicpython',
        'mitaki28.vscode-clang',
        'ms-azuretools.vscode-docker',
        'ms-python.python',
        'ms-vscode.cmake-tools',
        'ms-vscode.cpptools',
        'ms-vscode.csharp',
        'ms-vscode.powershell',
        'redhat.java',
        'redhat.vscode-yaml',
        'satoren.lualint',
        'sidthesloth.html5-boilerplate',
        'tobiah.comment-snippets',
        'tushortz.python-extended-snippets',
        'twxs.cmake',
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
        'max-SS.cyberpunk',
        'monokai.theme-monokai-pro-vscode',
        'ms-vscode.Theme-1337',
        'ms-vscode.theme-markdownkit',
        'ms-vscode.theme-materialkit',
        'pkief.material-icon-theme',
        'qinjia.seti-icons',
        'Scatolina.theme-monokaiextended',
        'sdras.night-owl',
        'sldobri.bunker',
        'smlombardi.darcula-extended',
        'stepanog.cage-icons',
        'syncap.sc-themes',
        'tushortz.theme-wildlife',
        'vangware.dark-plus-material',
        'vscode-icons-team.vscode-icons',
        'whizkydee.material-palenight-theme',
        'zhuangtongfa.material-theme',
    },
    'miscellaneous' : {
        'hoovercj.vscode-power-mode'
    },
    'experimental utils' : {
        'albymor.increment-selection',
        'Atlassian.atlascode',
        'axosoft.gitkraken-glo',
        'bb-spectacle.bb-spectacle',
        'Cardinal90.multi-cursor-case-preserve',
        'CoenraadS.bracket-pair-colorizer',
        'denco.confluence-markup',
        'gioboa.jira-plugin',
        'Gruntfuggly.todo-tree',
        'juliencroain.private-extension-manager',
        'letmaik.git-tree-compare',
        'lol2k.mirc',
        'marlon407.code-groovy',
        'olivier-grech.vscode-irc',
        'pstreule.codebucket',
        'RamiroBerrelleza.bitbucket-pull-requests',
        'rogalmic.bash-debug',
        'secanis.jenkinsfile-support',
        'SimonSiefke.svg-preview',
        'yo-C-ta.insert-multiple-rows',
    }
}

def _github_release_downloader(user, project, assets):
    url = 'https://github.com/{user}/{project}/releases/latest'.format(user=user, project=project)

    asset_base_url = 'https://github.com/{user}/{project}/releases/download/{{tag}}/{{asset}}'.format(user=user, project=project)
    code_base_url = 'https://github.com/{user}/{project}/archive/{{tag}}.{{archive}}'.format(user=user, project=project)

    def _downloader(driver):
        driver.get(url)

        tag = re.search(r'https://github\.com/[^/]+/[^/]+/releases/tag/(?P<tag>.+)', driver.current_url).groupdict()['tag']
        for asset in assets:
            driver.get(asset_base_url.format(tag=tag, asset=asset.format(tag=tag)))
        driver.get(code_base_url.format(tag=tag, archive='tar.gz'))

        return assets + [re.compile(r'.*-{tag}\.tar\.gz$'.format(tag=tag.replace('.', r'\.').replace('v', r'v?')), re.I)]

    return _downloader

def _asset_names(prefix, suffix, names):
    return [prefix + name + suffix for name in names]

def _multiple(*downloaders):
    def _downloader(driver):
        return itertools.chain(*(downloader(driver) for downloader in downloaders))
    return _downloader

def _null_downloader(driver):
    pass

_SPECIAL_EXTENSIONS = {
    'ms-vscode.cpptools' : {
        'downloader' : _github_release_downloader('Microsoft', 'vscode-cpptools',
                                                  _asset_names('cpptools-', '.vsix', ('linux', 'win32')))
    },
    'ms-vscode.csharp' : {
        'run_default' : True,
        'downloader' : _github_release_downloader('OmniSharp', 'omnisharp-roslyn',
                                                  _asset_names('omnisharp-', '.zip', ('linux-x64', 'win-x64', 'win-x86')))
    },
    'Gruntfuggly.todo-tree' : {
        'run_default' : True,
        'downloader' : _github_release_downloader('BurntSushi', 'ripgrep',
                                                  ['ripgrep_{tag}_amd64.deb'] +
                                                  _asset_names('ripgrep-{tag}-x86_64-', '', ('unknown-linux-musl.tar.gz', 'pc-windows-msvc.zip')))
    }
}

def extension_url(extension_name):
    '''
    Creates the extension's Visual Studio Code Maketplace URL.

    @param extension_name   The extension's name as refered by vscode in the format:
                            '{author}.{name}'.

    @return str
    '''
    return 'https://marketplace.visualstudio.com/items?itemName={}'.format(extension_name)

def all_extensions():
    '''
    Returns an iterable object that iterates through all listed extensions.

    @return An iterable object
    '''
    return (ext for category in _EXTENSIONS_BY_CATEGORIES
                for ext in _EXTENSIONS_BY_CATEGORIES[category])

def get_category(extension_name):
    '''
    Gets the name of category of the given extension.

    @param extension_name   The name of the extension to check.

    @return str
    '''
    for category in _EXTENSIONS_BY_CATEGORIES:
        if extension_name in _EXTENSIONS_BY_CATEGORIES[category]:
            return category
    return 'unknown'

def to_dirname(category):
    '''
    Converts a category's name to a directory name (in CamelCase).

    @param category A category's name.

    @return str
    '''
    return ''.join(word.capitalize() for word in category.split())

def _get_download_button(driver):
    for i in xrange(1000): # 1000 tries
        elements = driver.find_elements_by_css_selector('button[aria-label="Download Extension"]')
        if elements:
            return elements[0]
        time.sleep(1)

def _get_matcher(filename):
    if isinstance(filename, str):
        return lambda x: filename == x
    else:
        return filename.match

def _check_for_file(filename, download_path):
    match = _get_matcher(filename)

    return any(match(existing_file) for existing_file in os.listdir(download_path))

def _get_filename(filename, download_path):
    match = _get_matcher(filename)

    for existing_file in os.listdir(download_path):
        if match(existing_file):
            return existing_file

def _wait_for_file(filename, download_path):
    import sys
    if isinstance(filename, str):
        print('Waiting for', repr(filename))
    else:
        print('Waiting for regex', repr(filename.pattern))
    sys.stdout.flush()
    while not _check_for_file(filename, download_path):
        time.sleep(1)
        if os.path.exists(os.path.join(download_path, 'stop.txt')):
            return

class _Downloader():
    def __init__(self,
                 download_path=DOWNLOAD_BASE_PATH,
                 vscode_path=DOWNLOAD_INSTALLER_PATH,
                 extensions_path=DOWNLOAD_EXTENSIONS_PATH,
                 use_categories=True):
        self._download_path = download_path
        self._code_path = vscode_path
        self._ext_path = extensions_path
        self._use_categories = use_categories
        self._installers_in_progress = []
        self._exts_in_progress = []
        self._special_exts_in_progress = {}

        common.create_downloads(self._code_path, clean=False)
        common.create_downloads(self._ext_path, clean=False)

        options = webdriver.ChromeOptions()

        options.add_experimental_option("prefs", {
            "download.default_directory": self._download_path,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True
        })
        options.add_argument("--incognito")

        self._driver = webdriver.Chrome(chrome_options=options)

    def _download_vscode_for_os(self, os_button_name):
        self._driver.get('https://code.visualstudio.com/download')
        self._driver.find_element_by_css_selector('button[data-os={}]'.format(os_button_name)).click()
        time.sleep(1)

    def download_vscode(self):
        '''
        Download Visual Studio Code installers for Debian and Windows.
        '''
        self._download_vscode_for_os('linux64_deb')
        self._installers_in_progress.append(re.compile(r'.*\.deb$', re.I))
        self._download_vscode_for_os('win')
        self._installers_in_progress.append(re.compile(r'.*\.exe$', re.I))

    def _move_file_to_dest(self, dst_path, filename):
        common.create_downloads(dst_path, clean=False)

        src = os.path.join(self._download_path, filename)
        dst = os.path.join(dst_path, filename)
        shutil.move(src, dst)

    def _wait_for_installers(self):
        for installer in self._installers_in_progress:
            _wait_for_file(installer, self._download_path)

            self._move_file_to_dest(self._code_path, _get_filename(installer, self._download_path))

    def _default_download_extension(self, extension_name):
        self._driver.get(extension_url(extension_name))
        assert self._driver.title.endswith(' - Visual Studio Marketplace')
        real_extension_name, = re.search(r'itemName=([^?&]+)', self._driver.current_url.encode('utf-8')).groups()

        if real_extension_name != extension_name:
            print("\033[1;31mExtension name changed: {!r} -> {!r}".format(extension_name, real_extension_name))

        _get_download_button(self._driver).click()
        time.sleep(0.5)

        self._exts_in_progress.append((extension_name, real_extension_name))

    def download_extension(self, extension_name):
        '''
        Download Visual Studio Code extension.

        @param extension_name   The extension to download.
        '''
        print("Downloading {}...".format(extension_name))
        if extension_name in _SPECIAL_EXTENSIONS:
            ext_data = _SPECIAL_EXTENSIONS[extension_name]
            if ext_data.get('run_default', False):
                self._default_download_extension(extension_name)

            self._special_exts_in_progress[extension_name] = \
                ext_data.get('downloader', _null_downloader)(self._driver)
        else:
            self._default_download_extension(extension_name)

    def download_extensions(self, extensions):
        '''
        Download Visual Studio Code extensions.

        @param extensions   An iterable with the extensions to download.
        '''
        for ext in extensions:
            self.download_extension(ext)

    @staticmethod
    def _get_extension_re(extension_name):
        return re.compile(_EXTENSION_FILE_BASE_RE.format(name=extension_name), re.I)

    def _get_extension_filename(self, extension_name):
        return _get_filename(self._get_extension_re(extension_name), self._download_path)

    def _get_extension_dirname(self, extension_name):
        if self._use_categories:
            return os.path.join(self._ext_path, to_dirname(get_category(extension_name)))
        else:
            return self._ext_path

    def _wait_for_extension(self, extension_name, real_name=None):
        expected_name = real_name if real_name is not None else extension_name
        _wait_for_file(self._get_extension_re(expected_name), self._download_path)

        dst_path = self._get_extension_dirname(extension_name)
        filename = self._get_extension_filename(expected_name)

        self._move_file_to_dest(dst_path, filename)

    def _wait_for_all_extensions(self):
        for ext, name in self._exts_in_progress:
            self._wait_for_extension(ext, real_name=name)

    def _wait_for_extension_extra_file(self, extension_name, filename):
        _wait_for_file(filename, self._download_path)

        dst_path = os.path.join(self._get_extension_dirname(extension_name), extension_name)
        filename = _get_filename(filename, self._download_path)

        self._move_file_to_dest(dst_path, filename)

    def _wait_for_all_extensions_extra_files(self):
        for ext in self._special_exts_in_progress:
            for filename in self._special_exts_in_progress[ext]:
                self._wait_for_extension_extra_file(ext, filename)

    def _wait_for_downloads(self):
        self._wait_for_all_extensions()
        self._wait_for_all_extensions_extra_files()
        self._wait_for_installers()

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

def download_vscode(download_path=DOWNLOAD_BASE_PATH,
                    installer_path=DOWNLOAD_INSTALLER_PATH,
                    extensions_path=DOWNLOAD_EXTENSIONS_PATH,
                    use_categories=True):
    '''
    Download Visual Studio Code installers for Debian and Windows.
    '''
    print("Downloading: Visual Studio Code")

    with _Downloader(download_path=download_path,
                     vscode_path=installer_path,
                     extensions_path=extensions_path,
                     use_categories=use_categories) as downloader:
        downloader.download_extension(extension_name)

def download_extension(extension_name,
                       download_path=DOWNLOAD_BASE_PATH,
                       installer_path=DOWNLOAD_INSTALLER_PATH,
                       extensions_path=DOWNLOAD_EXTENSIONS_PATH,
                       use_categories=True):
    '''
    Download Visual Studio Code extension.

    @param extension_name   The extension to download.
    '''
    print("Downloading: ", extension_name)

    with _Downloader(download_path=download_path,
                     vscode_path=installer_path,
                     extensions_path=extensions_path,
                     use_categories=use_categories) as downloader:
        downloader.download_extension(extension_name)

def download_extensions(extensions,
                        download_path=DOWNLOAD_BASE_PATH,
                        installer_path=DOWNLOAD_INSTALLER_PATH,
                        extensions_path=DOWNLOAD_EXTENSIONS_PATH,
                        use_categories=True):
    '''
    Download Visual Studio Code extensions.

    @param extensions   An iterable with the extensions to download.
    '''
    print("Downloading: ", ', '.join(extensions))

    with _Downloader(download_path=download_path,
                     vscode_path=installer_path,
                     extensions_path=extensions_path,
                     use_categories=use_categories) as downloader:
        downloader.download_extensions(extensions)

if __name__ == '__main__':
    common.create_downloads(DOWNLOAD_BASE_PATH)

    with _Downloader() as downloader:
        downloader.download_extensions(all_extensions())
        downloader.download_vscode()
