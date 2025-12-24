import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.views.decorators.cache import cache_page


ULTIMATES = {
    'ucob': 'The Unending Coil of Bahamut (Ultimate)',
    'uwu':  'The Weapon\'s Refrain (Ultimate)',
    'tea':  'The Epic of Alexander (Ultimate)',
    'dsr':  'Dragonsong\'s Reprise (Ultimate)',
    'top':  'The Omega Protocol (Ultimate)',
    'fru':  'Futures Rewritten (Ultimate)', 
}

def home(request):
    return render(request, 'index.html')

def pf_page(request, raid_slug):
    target_duty = ULTIMATES.get(raid_slug.lower())
    if not target_duty:
        return render(request, 'index.html')

    # Solo enviamos info básica para pintar la pantalla
    context = {
        'raid_name': target_duty,
        'raid_slug': raid_slug
    }
    return render(request, 'pf_index.html', context)

def pf_results(request, raid_slug):
    target_duty = ULTIMATES.get(raid_slug.lower())
    

    URL_XIVPF = 'https://xivpf.com/listings'
    headers = {'User-Agent': 'Mozilla/5.0'}
    NA_DCS = ['Aether', 'Primal', 'Crystal', 'Dynamis']
    pf_data = []
    
    try:
        response = requests.get(URL_XIVPF, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        raw_listings = soup.select('#listings .listing')

        for item in raw_listings:
            datacenter = item.get('data-centre', 'Unknown')
            if datacenter not in NA_DCS: continue
            
            duty_elem = item.find(class_='duty')
            duty_text = duty_elem.get_text(strip=True) if duty_elem else ''
            
            if target_duty.lower() not in duty_text.lower(): continue

            desc_elem = item.find(class_='description')
            creator_elem = item.find(class_='creator')
            
            pf_data.append({
                'duty': duty_text,
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'creator': creator_elem.get_text(strip=True) if creator_elem else 'Anon',
                'datacenter': datacenter,
            })
    except Exception:
        pass

    return render(request, 'partials/rows.html', {'listings': pf_data})