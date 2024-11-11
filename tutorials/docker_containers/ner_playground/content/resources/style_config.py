import os
here_pth = os.path.abspath(os.path.dirname(__file__))

#APP STYLE
MAX_WIDTH = 1600
PADDING_TOP = 1
PADDING_BOTTOM = 1
PADDING_RIGHT = 4
PADDING_LEFT = 4
COLOR = 'black'
BACKGROUND_COLOR = 'white'

HTML_WRAPPER = """<div class="scroll entities" style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem; white-space:pre-wrap">{}</div>"""
HTML_INDEX_WRAPPER = """<div ">{}</div>"""

STYLE_CONFIG_OLD = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    *:not(text){{
      font-family: Montserrat;
    }}
    
    .reportview-container .main .block-container{{
        max-width: {MAX_WIDTH}px;
        padding-top: {PADDING_TOP}rem;
        padding-right: {PADDING_RIGHT}rem;
        padding-left: {PADDING_LEFT}rem;
        padding-bottom: {PADDING_BOTTOM}rem;
    }}
    .reportview-container .main {{
        color: {COLOR};
        background-color: {BACKGROUND_COLOR};
    }}
    div.scroll {{ 
                margin:4px, 4px; 
                padding:4px; 
                width: 100%; 
                height: 500px; 
                overflow-x: hidden; 
                overflow-x: auto;  
    }}
    .entity-wrapper{{
        padding: 5px;
        display: inline-grid;
        text-align:center;
        margin-bottom:5px;
        border-radius: 5px 5px
    }}
    .entity-name{{
        background: #f1f2f3;
        color: #3c3e44;
        padding: 2px;
        border-color: #484b51;
        border-width: medium;
        border-radius: 5px 5px;
    }}
    .entity-type{{
        color: #272727;
        text-transform: uppercase;
        font-family: roboto;
        font-size: 13px;
    }}
    .reportview-container .markdown-text-container{{
        font-family: roboto !important;
        color: dimgray !important;
        line-height: normal !important;
    }}
    .reportview-container h2
    {{
        font-weight: 400 !important;
        font-size: 1.5rem !important;
        line-height: 1.6!important;
    }}
    .reportview-container h2
    {{
        font-weight: 300 !important;
        font-size: 1.3rem !important;
        line-height: 1.4!important;
    }}
    
    
</style>
"""

with open(here_pth+'/style.css') as f:
    STYLE_CONFIG_NEW = f.read()
STYLE_CONFIG = STYLE_CONFIG_OLD + '<style>{}</style>'.format(STYLE_CONFIG_NEW)