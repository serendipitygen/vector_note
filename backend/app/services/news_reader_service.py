import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_content_from_url(url:str):
    """
    URL에서 기사 본문을 추출합니다.
    다양한 예외처리와 정제 로직을 포함합니다.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements more aggressively
        unwanted_elements = [
            'script', 'style', 'nav', 'footer', 'header', 'aside',
            'iframe', '.copyright', '.reporter-info', '.social-share',
            '.related-news', '.article-footer', '.article-bottom',
            '.feedback', '.rating', '.navigation', '.reporter',
            '.copyright_area', '.byline', '.social-plugins',
            '.article-sns', '.article-tools', '.article-tags',
            '.article-meta', '.article-navigation', '.article-footer-wrap',
            '[class*="share"]', '[class*="copyright"]', '[class*="sns"]',
            '[class*="social"]', '[class*="reply"]', '[class*="comment"]'
        ]
        
        for element in soup.select(','.join(unwanted_elements)):
            element.decompose()

        # Dictionary of domain-specific article content selectors
        domain_selectors = {
            'mk.co.kr': '.article_body',
            'news.naver.com': '#dic_area',
            'hankyung.com': '.article-body',
            'chosun.com': '.article-body',
            'donga.com': '.article_txt',
            'yna.co.kr': '.story-news',
            'mbc.co.kr': '.article_content',
            'bok.or.kr': '.contents_body'
        }

        domain = urlparse(url).netloc
        article_content = None

        for domain_key, selector in domain_selectors.items():
            if domain_key in domain:
                content_element = soup.select_one(selector)
                if content_element:
                    for unwanted in content_element.select('.reporter_area, .copyright, .byline, .social-share'):
                        unwanted.decompose()
                    article_content = content_element.get_text(strip=True)
                    break

        if not article_content:
            content_selectors = [
                'article .content', '.article_content', '.article-content',
                '.news_content', '.news-content', '[itemprop="articleBody"]',
                '.article-body-content'
            ]
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    for unwanted in content.select('.reporter_area, .copyright, .byline, .social-share'):
                        unwanted.decompose()
                    article_content = content.get_text(strip=True)
                    break

        if not article_content:
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                for element in main_content.find_all(['aside', 'nav', '.related-articles', '.article-links', '.news-list']):
                    element.decompose()
                article_content = main_content.get_text(strip=True)

        if not article_content:
            return f"원본 URL: {url}\n\n내용을 자동으로 추출하지 못했습니다. 수동으로 내용을 복사하여 붙여넣어 주세요."

        article_content = ' '.join(article_content.split())
        
        remove_patterns = [
            r'관련기사', r'많이본 기사', r'추천기사', r'댓글', r'기자 바로가기', r'공유하기',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'저작권자.*$', r'무단전재', r'재배포금지', r'\(c\)', r'©', r'copyright', r'Copyright',
            r'\w+\s*기자', r'\w+\s*특파원', r'작성자', r'편집자',
            r'카카오톡', r'페이스북', r'트위터', r'링크드인',
            r'유용한 정보가 되었나요\?', r'매우만족', r'만족', r'보통', r'불만족', r'매우불만족',
            r'목록', r'이전', r'다음', r'페이지 위로 이동',
            r'제보는', r'뉴스는 24시간', r'내가 본 콘텐츠',
            r'▲.*?▲', r'■.*?■',
        ]
        
        for pattern in remove_patterns:
            article_content = re.sub(pattern, '', article_content, flags=re.IGNORECASE)
        
        article_content = article_content.strip()
        article_content = ' '.join(article_content.split())
        
        return article_content
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return f"원본 URL: {url}\n\n기사 내용을 추출하는 중 오류가 발생했습니다: {e}" 