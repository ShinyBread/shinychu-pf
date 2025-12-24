import requests
import logging
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN ---
ULTIMATES = {
    'ucob': 'The Unending Coil of Bahamut (Ultimate)',
    'uwu':  'The Weapon\'s Refrain (Ultimate)',
    'tea':  'The Epic of Alexander (Ultimate)',
    'dsr':  'Dragonsong\'s Reprise (Ultimate)',
    'top':  'The Omega Protocol (Ultimate)',
    'fru':  'Futures Rewritten (Ultimate)', 
}

URL_XIVPF = 'https://xivpf.com/listings'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
NA_DCS = ['Aether', 'Primal', 'Crystal', 'Dynamis']


JOB_MAP = {

    'PLD': 'Paladin_Icon_1.png',
    'WAR': 'Warrior_Icon_1.png',
    'DRK': 'Dark_Knight_Icon_1.png',
    'GNB': 'Gunbreaker_Icon_1.png',
    'GLA': 'Gladiator_Icon_1.png',
    'MRD': 'Marauder_Icon_1.png',
    
    'WHM': 'White_Mage_Icon_1.png',
    'SCH': 'Scholar_Icon_1.png',
    'AST': 'Astrologian_Icon_1.png',
    'SGE': 'Sage_Icon_1.png',
    'CNJ': 'Conjurer_Icon_1.png',

    'MNK': 'Monk_Icon_1.png',
    'DRG': 'Dragoon_Icon_1.png',
    'NIN': 'Ninja_Icon_1.png',
    'SAM': 'Samurai_Icon_1.png',
    'RPR': 'Reaper_Icon_1.png',
    'VPR': 'Viper_Icon_1.png',
    'PGL': 'Pugilist_Icon_1.png',
    'LNC': 'Lancer_Icon_1.png',
    'ROG': 'Rogue_Icon_1.png',

    'BRD': 'Bard_Icon_1.png',
    'MCH': 'Machinist_Icon_1.png',
    'DNC': 'Dancer_Icon_1.png',
    'ARC': 'Archer_Icon_1.png',


    'BLM': 'Black_Mage_Icon_1.png',
    'SMN': 'Summoner_Icon_1.png',
    'RDM': 'Red_Mage_Icon_1.png',
    'PCT': 'Pictomancer_Icon_1.png',
    'BLU': 'Blue_Mage_Icon_1.png',
    'THM': 'Thaumaturge_Icon_1.png',
    'ACN': 'Arcanist_Icon_1.png',

    'CRP': 'Carpenter_Icon_1.png',
    'BSM': 'Blacksmith_Icon_1.png',
    'ARM': 'Armorer_Icon_1.png',
    'GSM': 'Goldsmith_Icon_1.png',
    'LTW': 'Leatherworker_Icon_1.png',
    'WVR': 'Weaver_Icon_1.png',
    'ALC': 'Alchemist_Icon_1.png',
    'CUL': 'Culinarian_Icon_1.png',


    'MIN': 'Miner_Icon_1.png',
    'BTN': 'Botanist_Icon_1.png',
    'FSH': 'Fisher_Icon_1.png',
}

def fetch_xivpf_listings(target_duty_name):
    pf_data = []
    try:
        response = requests.get(URL_XIVPF, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        raw_listings = soup.select('#listings .listing')

        for item in raw_listings:
            datacenter = item.get('data-centre', 'Unknown')
            if datacenter not in NA_DCS: continue
            
            duty_elem = item.find(class_='duty')
            duty_text = duty_elem.get_text(strip=True) if duty_elem else ''
            if target_duty_name.lower() not in duty_text.lower(): continue

            desc_elem = item.find(class_='description')
            creator_elem = item.find(class_='creator')

            slots_data = []
            filled_count = 0
            
            party_elem = item.find(class_='party')
            if party_elem:
                raw_slots = party_elem.select('.slot')
                for slot in raw_slots:
                    classes = slot.get('class', [])
                    raw_title = slot.get('title', '').strip() 
                    
                    is_filled = 'filled' in classes
                    if is_filled: filled_count += 1
                    role_class = 'any'
                    if 'tank' in classes: role_class = 'tank'
                    elif 'healer' in classes: role_class = 'healer'
                    elif 'dps' in classes: role_class = 'dps'
                    icon_filename = None
                    if is_filled and raw_title in JOB_MAP:
                        icon_filename = JOB_MAP[raw_title]
                    slots_data.append({
                        'is_image': bool(icon_filename),
                        'image_file': icon_filename,
                        'css_classes': f"{role_class} {'filled' if is_filled else 'empty'}",
                        'title': raw_title
                    })
            
            if not slots_data:
                slots_data = [{'is_image': False, 'css_classes': 'empty', 'title': 'Unknown'}] * 8

            pf_data.append({
                'datacenter': datacenter,
                'duty': duty_text,
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'creator': creator_elem.get_text(strip=True) if creator_elem else 'Unknown',
                'slots': slots_data,
                'slots_count': f"{filled_count}/8"
            })

    except Exception as e:
        logger.error(f"Error scraping XIVPF: {e}")
        return []

    return pf_data


def home(request): return render(request, 'index.html')

def pf_page(request, raid_slug):
    target_duty = ULTIMATES.get(raid_slug.lower())
    if not target_duty: return render(request, 'index.html')
    return render(request, 'pf_index.html', {'raid_name': target_duty, 'raid_slug': raid_slug})

@cache_page(60 * 1)
def pf_results(request, raid_slug):
    target_duty = ULTIMATES.get(raid_slug.lower())
    if not target_duty: return HttpResponse("")
    listings = fetch_xivpf_listings(target_duty)
    return render(request, 'partials/rows.html', {'listings': listings})