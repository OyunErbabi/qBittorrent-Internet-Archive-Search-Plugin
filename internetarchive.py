# -*- coding: utf-8 -*-
# VERSION: 1.0
# AUTHORS: OyunErbabi

import json
import math
import urllib.request
import urllib.parse
import urllib.error
from novaprinter import prettyPrinter

class internetarchive(object):
    name = "Internet Archive"
    url = "https://archive.org"
    supported_categories = {'all': 'all'}
    
    def convert_size(self, size_bytes):
        
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def retrieve_url(self, url):
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
                
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            raise
        except Exception as e:
            print(f"Error retrieving URL: {e}")
            raise   

    def search(self, what, cat='all'):
        
        what_decoded = urllib.parse.unquote(what)
        what_encoded = what_decoded.replace(' ', '+')
        
        page = 1
        has_more_results = True
        result_count = 0
        
        while has_more_results:
            search_url = f"https://archive.org/advancedsearch.php?q={what_encoded}&output=json&rows=50&page={page}&fl[]=identifier,title,format,item_size"
            
            try:
                response_text = self.retrieve_url(search_url)
                data = json.loads(response_text)
            except Exception as e:
                print(f"Error retrieving or parsing data: {e}")
                return

            docs = data.get('response', {}).get('docs', [])
            if not docs:
                has_more_results = False
                if page == 1 and result_count == 0:
                    print("No results found")
                break

            for doc in docs:
                identifier = doc.get('identifier')
                if not identifier:
                    continue                   
                
                formats = doc.get('format', [])
                has_torrent = any("BitTorrent" in str(f) for f in formats)
                if not has_torrent:
                    continue
                    
                
                item_size_bytes = doc.get('item_size', 0)
                size_str = self.convert_size(item_size_bytes)
                    
                
                title = doc.get('title', identifier)
                if isinstance(title, list):
                    title = title[0] if title else identifier
                    
                result = {
                    'name': title,
                    'link': f"https://archive.org/download/{identifier}/{identifier}_archive.torrent",
                    'size': size_str,
                    'seeds': '-1',
                    'leech': '-1',
                    'engine_url': self.url,
                    'desc_link': f"https://archive.org/details/{identifier}"
                }
                prettyPrinter(result)
                result_count += 1
            
            page += 1
            
            if result_count >= 200:
                print("Reached maximum result limit (200 items)")
                break
            
            total_results = data.get('response', {}).get('numFound', 0)
            if page * 50 >= total_results:
                has_more_results = False