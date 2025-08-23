
i_was_bored = r"""



.__                           ___.                            .___                 
|__| __  _  _______    ______ \ _|__   ___________   ____   __| _/   ______ ___.__.
|  | \ \/ \/ /\__  \  /  ___/  | __ \ /  _ \_  __ \_/ __ \ / __ |    \____ <   |  |
|  |  \     /  / __ \_\___ \   | \_\ (  <_> )  | \/\  ___// /_/ |    |  |_> >___  |
|__|   \/\_/  (____  /____  >  |___  /\____/|__|    \___  >____ | /\ |   __// ____|
                   \/     \/       \/                   \/     \/ \/ |__|   \/    

                   
                i_was_bored.py - A Text-Based Rouge-like RPG
                            Enter 를 눌러 계속...
                                help - 도움말
                                

"""
help_text = r"""

1. 개요
    - 이 게임은 파이썬으로 만든 텍스트 기반 로그라이크 RPG입니다.
    - 플레이어는 몬스터와 싸우고, 장비를 수집하며, 스킬을 사용해 생존을 목표로 합니다.
    - 게임은 턴제 전투 시스템을 사용하며, 다양한 상태이상과 스킬 효과가 존재합니다.
2. 힘
    - 기술과 일맥상통합니다. 공격, 방어, 상태이상 부여 등 다양한 효과를 가집니다.
    - 각 스킬은 레벨과 사용 횟수가 있으며, 사용 횟수가 0이 되면 더 이상 사용할 수 없습니다.
    - 스킬은 전투 중에 전략적으로 사용해야 합니다.
3. 적
    - 몬스터는 각기 다른 능력치와 스킬을 가지고 있습니다.
    - 보스 몬스터는 더 강력한 능력치와 스킬을 가지고 있으며 처치시 상점으로 이동하고 다음 장으로 넘어갑니다.


                            Enter 를 눌러 게임 시작...
"""

import random
import time

# --- 상태이상 클래스 ---
class StatusEffect:
    def __init__(self, name, duration, 
                 damage_per_turn=0, 
                 attack_modifier=0, defense_modifier=0, evasion_modifier=0,
                 damage_taken_modifier=0, damage_dealt_modifier=0,
                 ignore_defense=False, ignore_evasion=False, skip_turn=False,
                 invincible=False):
        self.name = name
        self.duration = duration
        self.damage_per_turn = damage_per_turn
        self.attack_modifier = attack_modifier
        self.defense_modifier = defense_modifier
        self.evasion_modifier = evasion_modifier
        self.damage_taken_modifier = damage_taken_modifier
        self.damage_dealt_modifier = damage_dealt_modifier
        self.ignore_defense = ignore_defense
        self.ignore_evasion = ignore_evasion
        self.skip_turn = skip_turn
        self.invincible = invincible

    def apply_effect(self, target):
        if self.damage_per_turn > 0:
            target.take_damage(self.damage_per_turn)

# --- 스킬 클래스 ---
class Skill:
    def __init__(self, name, level, max_level, rarity, use_count, effect, is_monster_only=False,power=1.0):
        self.name = name
        self.level = level
        self.max_level = max_level
        self.rarity = rarity
        self.use_count = use_count
        self.initial_use_count = use_count
        self.effect = effect
        self.is_monster_only = is_monster_only
        self.power = power

    def execute(self, caster, target):
        self.use_count -= 1
        self.effect(caster, target, self)

    def reset_use_count(self):
        self.use_count = self.initial_use_count

# --- 장비 클래스 ---
class Equipment:
    def __init__(self, name, part, stage, health=0, attack=0, defense=0, price=0, critical=0, evasion=0):
        self.name = name
        self.part = part
        self.stage = stage
        self.health = health
        self.attack = attack
        self.defense = defense
        self.price = price
        self.critical = critical
        self.evasion = evasion

# --- 캐릭터 기본 클래스 ---
class Character:
    def __init__(self, name, max_health, attack, defense, evasion, critical):
        self.name = name
        self.max_health = max_health
        self.current_health = max_health
        self.attack = attack
        self.defense = defense
        self.evasion = evasion
        self.critical = critical
        self.skills = []
        self.status_effects = []

        self._base_attack = attack
        self._base_defense = defense
        self._base_evasion = evasion

    def is_alive(self):
        return self.current_health > 0

    def take_damage(self, damage):
        is_invincible = any(e.invincible for e in self.status_effects)
        if is_invincible:
            print(f"{self.name}의 육신은 상처를 거부했다.")
            return

        # Evasion Calculation
        evasion_chance = self.evasion / 100
        # Cap evasion at 70%
        evasion_chance = min(evasion_chance, 70 / 100) 
        if random.random() < evasion_chance:
            print(f"{self.name}이(가) 공격을 회피했다!")
            return

        ignore_defense_active = any(e.ignore_defense for e in self.status_effects)
        damage_taken_multiplier = 1.0 + sum(e.damage_taken_modifier for e in self.status_effects)

        calculated_defense = 0 if ignore_defense_active else self.defense

        # 데미지 계산
        actual_damage = max(1, round(damage / (1 + calculated_defense / 100)))
        actual_damage = round(actual_damage * damage_taken_multiplier)

        self.current_health -= actual_damage
        print(f"{self.name}의 살점이 {actual_damage}만큼 찢겨나갔다. (남은 생명: {self.current_health}/{self.max_health})")
        if not self.is_alive():
            print(f"{self.name}의 마지막 숨이 멎었다.")
            time.sleep(1)

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)
        print(f"{self.name}이(가) {amount}만큼 생명을 되찾았다. (현재 생명: {self.current_health}/{self.max_health})")

    def deal_damage(self, target, base_damage, is_skill=False):
        critical_multiplier = 1.0
        if random.random() < self.critical / 100:
            critical_multiplier = 2.0 # 치명타 배율
            print(f"{self.name}의 공격이 {target.name}에게 치명타로 적중했다!")
        
        final_damage = base_damage * critical_multiplier
        target.take_damage(final_damage)


    # 스탯 부여
    def add_status_effect(self, effect):
        self.status_effects = [e for e in self.status_effects if e.name != effect.name]
        self.status_effects.append(effect)
        print(f"{self.name}에게 {effect.name}의 낙인이 찍혔다. (지속: {effect.duration}턴)")
        self._apply_stat_modifiers()

    # 스탯 강화 적용
    def _apply_stat_modifiers(self):
        self.attack = self._base_attack
        self.defense = self._base_defense
        self.evasion = self._base_evasion

        for effect in self.status_effects:
            self.attack += effect.attack_modifier
            self.defense += effect.defense_modifier
            self.evasion += effect.evasion_modifier

    # 턴 효과 적용
    def apply_turn_effects(self):
        skip_turn_active = False
        for effect in self.status_effects[:]:
            print(f"{self.name}은(는) {effect.name}의 영향을 받고 있다. (남은 턴: {effect.duration})")
            if effect.skip_turn:
                skip_turn_active = True
                print(f"{self.name}은(는) {effect.name}의 속박되어 움직이지 못했다.")
                effect.duration -= 1
            if effect.duration == 0:
                self.status_effects.remove(effect)
                print(f"{self.name}의 {effect.name} 낙인이 희미해진다.")
                return True

            if effect.damage_per_turn > 0:
                print(f"{effect.name}이(가) {self.name}의 생명을 갉아먹는다.")
                self.take_damage(effect.damage_per_turn)
            
            effect.duration -= 1
            if effect.duration < 0:
                self.status_effects.remove(effect)
                print(f"{self.name}의 {effect.name} 낙인이 사라졌다.")
                self._apply_stat_modifiers()
        return False

    def show_stats(self):
        print(f"\n[ {self.name} ]")
        print(f"생명: {self.current_health}/{self.max_health}")
        print(f"공격: {self.attack} 방어: {self.defense}")
        print(f"민첩: {self.evasion * 100} 강타: {self.critical * 100}")
        time.sleep(1)
    def show_inv(self):
        if isinstance(self, Player):
            print("[ 장비 ]")
            for part, item in self.equipment.items():
                print(f"{part}: {item.name if item else '없음'}")
            print("[ 힘 ]")
            if self.skills:
                for skill in self.skills:
                    print(f"{skill.name} (Lv.{skill.level}, 남은 횟수: {skill.use_count})")
            else:
                print("습득한 힘 없음")
# --- 플레이어 클래스 ---
class Player(Character):
    def __init__(self, name):
        super().__init__(name, 100, 10, 5, 10, 10)
        self.equipment = {"무기": None, "투구": None, "흉갑": None, "각반": None, "장신구": None}
        self.gold = 0

    def equip(self, item):
        if self.equipment[item.part]:
            self.unequip(item.part)
        self.equipment[item.part] = item
        self.max_health += item.health
        self.current_health += item.health
        self.attack += item.attack
        self.defense += item.defense
        self.critical += item.critical
        self.evasion += item.evasion
        print(f"{item.name}을(를) 착용했다.")
        self.show_stats()
        self.show_inv()

    def unequip(self, part):
        item = self.equipment[part]
        if item:
            self.max_health -= item.health
            self.attack -= item.attack
            self.defense -= item.defense
            self.critical -= item.critical
            self.evasion -= item.evasion
            if self.current_health > self.max_health:
                self.current_health = self.max_health
            self.equipment[part] = None
            print(f"{item.name}을(를) 벗었다.")

# --- 몬스터 클래스 ---
class Monster(Character):
    def __init__(self, name, stage, is_boss, max_health, attack, defense, evasion, critical, gold, skills=None):
        super().__init__(name, max_health, attack, defense, evasion, critical)
        self.stage = stage
        self.is_boss = is_boss
        self.gold = gold
        self.skills = skills if skills else []

# --- 게임 클래스 ---
class Game:
    def __init__(self):
        self.player = Player("방랑자(당신)")
        self.stage = 1
        self.battle_count = 0
        self.all_monsters = []
        self.all_equipment = []
        self.all_skills = []
        self.all_skills_map = {}
        self._initialize_data()

    def _initialize_data(self):
        self._initialize_skills()
        self._initialize_equipment()
        self._initialize_monsters()
# 스킬 구현부
    def _initialize_skills(self):

        # 기본 데미지 스킬
        def damage(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 살점을 도려낸다.")
            target.take_damage(caster.attack * (1 + skill.level/5) * skill.power)

        # 낮은 성장력 (power를 높혀주세요)
        def pulverize(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 뼈를 으깬다.")
            target.take_damage(caster.attack * (1 + skill.level/10) * skill.power)
    
        # 높은 스킬 성장력 attack * level * power
        def reaping(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 영혼을 부순다.")
            target.take_damage(caster.attack * skill.level * skill.power)

        # 고정 데미지 level * power
        def fixed_damage(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}을(를) 강하게 내려친다.")
            target.take_damage(skill.level * skill.power)
        
        # 낮은체력 대상 2배 데미지
        def execute(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 마지막 숨통을 끊는다.")
            damage = caster.attack * (1 + skill.level/5) * skill.power
            if target.current_health < target.max_health * 0.5:
                damage *= 2
            target.take_damage(damage)

        # 아주 높은 계수 caster.attack * 1.8 * power
        def advance_damage(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}을(를) 향해 일격을 날린다.")
            target.take_damage(caster.attack * 2 * skill.power * skill.level)

        # 두번 공격
        def flurry(caster, target, skill):
            print(f"'{skill.name}' 발동... 핏빛 칼날이 춤춘다.")
            target.take_damage(caster.attack * (0.5 + (skill.level / 5)))
            target.take_damage(caster.attack * (0.5 + (skill.level / 5)))

        # 생명력 흡수
        def life_steal(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 생명을 흡수한다.")
            caster.heal(caster.max_health * 0.2 * skill.level)
            target.take_damage(caster.attack * skill.level / 2)

        # 방어력 증가 10 * level * power
        def iron_will(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 고통을 감내한다.")
            caster.add_status_effect(StatusEffect("철의 의지", 3, defense_modifier=(10 * skill.level * skill.power)))

        # 공격력 증가 5 * level * power
        def war_cry(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}의 절규가 전장에 울린다.")
            caster.add_status_effect(StatusEffect("전투의 함성", 2, attack_modifier=(5 * skill.level * skill.power)))

        # 기절 skill.power 턴동안
        def stun(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}을(를) 무력화시킨다.")
            target.add_status_effect(StatusEffect("기절", int(skill.power), skip_turn=True))

        # 무적 power 턴동안
        def shadow(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 그림자가 된다.")
            caster.add_status_effect(StatusEffect("그림자 형상", skill.power, invincible=True))

        # 공격력 50% 증가 3턴 (상수)
        def frenzy(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 광란에 휩싸인다.")
            caster.add_status_effect(StatusEffect("광란", 3, attack_modifier=caster.attack * 0.5))

        # 매 턴 데미지 attack * 0.5 * level * power
        def exsanguinate(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 피를 말린다.")
            target.add_status_effect(StatusEffect("과다출혈", 3, damage_per_turn=caster.attack * 0.5 * skill.level * skill.power))

        # 적 데미지 50% 약화
        def cripple(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 힘줄을 끊는다.")
            target.add_status_effect(StatusEffect("불구", 2, attack_modifier=-target.attack * 0.5))
        
        # 약자 멸시 주는피해 받는피해 100% 증가 999턴 (상수)
        def scorn_the_weak(caster, target, skill):
            print(f"'{skill.name}' 발동... 약자는 죽어야 마땅하다.")
            target.add_status_effect(StatusEffect("약자멸시", 999, damage_taken_modifier=1.0, damage_dealt_modifier=1.0))

        # 효과 없음
        def taunt(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}을(를) 조롱한다......")
            pass

        # 적 데미지 20% 3턴 약화 (상수)
        def weaken(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}을(를) 약화시킨다.")
            target.add_status_effect(StatusEffect("약화", 3, attack_modifier=-target.attack * 0.2))

        # 받는 피해 20% 증가 3턴 (상수)
        def shatter_bone(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 뼈를 뒤틀어 놓는다.")
            target.add_status_effect(StatusEffect("골절", 3, damage_taken_modifier=0.2))

        # 받는피해 증가 
        def hex(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}에게 끔찍한 저주를 내린다.")
            target.add_status_effect(StatusEffect("저주", 3, damage_taken_modifier=skill.power))
        
        # 회피율증가 10 * level 3턴
        def fade(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}의 모습이 흐려진다.")
            caster.add_status_effect(StatusEffect("흐릿한 형상", 3, evasion_modifier=0.1 * skill.level))
        
        # 공격력 증가 power 턴 동안 1.5 + level / 2
        def hate(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 증오를 집중한다.")
            caster.add_status_effect(StatusEffect("증오 집중", skill.power, damage_dealt_modifier=(1.5 + skill.level / 2)))

        # 몬스터용
        def expose_weakness(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 약점을 드러낸다.")
            target.add_status_effect(StatusEffect("약점 노출", 2, ignore_defense=True))
        
        def blight(caster, target, skill):
            print(f"'{skill.name}' 발동... 부패의 구름이 {target.name}을(를) 감싼다.")
            target.add_status_effect(StatusEffect("부패", 5, damage_per_turn=caster.attack * 0.05 * skill.level))

        def drain_life(caster, target, skill):
            damage = caster.attack * 1.1
            print(f"'{skill.name}' 발동... {target.name}의 생명력을 흡수한다.")
            target.take_damage(damage)
            caster.heal(damage * 0.2 * skill.level)

        def silence(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 주문을 봉인한다.")
            target.add_status_effect(StatusEffect("침묵", 2))

        def reckless_abandon(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 모든 것을 내던진다.")
            caster.add_status_effect(StatusEffect("무모한 분노", 3, attack_modifier=15 * skill.level, defense_modifier=-10 * skill.level))

        def mirror_image(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}의 환영이 나타난다.")
            caster.add_status_effect(StatusEffect("거울 환영", 2, evasion_modifier=0.25 * skill.level))

            
        def bone_armor(caster, target, skill):
            print(f"'{skill.name}' 발동... 뼈 갑옷이 {caster.name}을(를) 감싼다. (방어력 + {20 * skill.level})")
            caster.add_status_effect(StatusEffect("뼈 갑옷", 2, defense_modifier=20 * skill.level))

        def ensnare(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}의 발을 옭아맨다. (민첩성 -{0.2 * skill.level})")
            target.add_status_effect(StatusEffect("올가미", 2, evasion_modifier=-0.2 * skill.level))
        
        # 최대체력 * 0.15 * level * power 만큼 회복
        def heal(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 죽음의 경계에서 생명을 얻는다.")
            caster.heal(caster.max_health * 0.15 * skill.level * skill.power)

        def thorn_mail(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 가시 돋친 갑옷을 입는다.")
            caster.add_status_effect(StatusEffect("가시 갑옷", 3, defense_modifier=5 * skill.level))
            
        def devour(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) {target.name}을(를) 집어삼키려 합니다!")
            damage = caster.attack * 2.5
            target.take_damage(damage)
            caster.heal(damage * 0.5)

        def fire_breath(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 화염을 내뿜는다.")
            target.take_damage(caster.attack * 1.5)

        def frost_breath(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 냉기를 내뿜는다.")
            target.take_damage(caster.attack * 1.5)
            target.add_status_effect(StatusEffect("빙결", 1, skip_turn=True))

        def poison_breath(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 독기를 내뿜는다.")
            target.add_status_effect(StatusEffect("중독", 3, damage_per_turn=caster.attack * 0.2))

        def whirlpool(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 소용돌이를 일으킨다.")
            target.take_damage(caster.attack * 1.2)
            target.add_status_effect(StatusEffect("속박", 2, evasion_modifier=-0.2))

        def pestilence(caster, target, skill):
            print(f"'{skill.name}' 발동... 역병이 퍼진다.")
            target.add_status_effect(StatusEffect("역병", 5, damage_per_turn=caster.attack * 0.2, attack_modifier=-5, defense_modifier=-5))

        def petrifying_gaze(caster, target, skill):
            print(f"'{skill.name}' 발동... {target.name}이(가) 돌처럼 굳어간다.")
            target.add_status_effect(StatusEffect("석화", 1, skip_turn=True, defense_modifier=50))
            
        def soul_drain_aura(caster, target, skill):
            print(f"'{skill.name}' 발동... {caster.name}이(가) 주변의 영혼을 흡수한다.")
            target.take_damage(caster.attack * 0.5)
            caster.heal(caster.attack * 0.5)

        def summon_abomination(caster, target, skill):
            print(f"'{skill.name}' 발동... 혐오스러운 존재를 소환한다.")
            caster.add_status_effect(StatusEffect("소환수와 함께", 99, attack_modifier=10))

        self.all_skills = [
           
        # 일반 등급 (1)

            #공격
            Skill("찌르기", 1, 2, 1, 99, damage, power=1.5),
            Skill("꿰뚫기", 1, 5, 1, 15, reaping, power=0.9),
            Skill("걷어차기", 1, 3, 1, 10, fixed_damage, power=20.0),
            Skill("기습", 1, 10, 1, 2, damage, power=1.5),

            #피흡
            Skill("물어 뜯기", 1, 2, 2, 3, life_steal, power=1.0),

            #스탯강화
            Skill("강철의 의지", 1, 3, 1, 3, iron_will, power=3.0),
            Skill("전쟁의 포효", 1, 3, 1, 3, war_cry, power=3.0),

            #효과
            Skill("약화", 1, 3, 1, 10, weaken, power=-0.2),
            Skill("기절시키기", 1, 2, 1, 10, stun, power=1.0),
            Skill("증오", 1, 3, 1, 5, hate, power=1.0),
            Skill("뼈 갑옷", 1, 3, 1, 2, bone_armor, power=20),
            Skill("올가미", 1, 2, 1, 3, ensnare, power=-0.2),
            Skill("응급 처치", 1, 3, 1, 1, heal, power=1.0),
            Skill("가시 갑옷", 1, 3, 1, 3, thorn_mail, power=1.0),

            # 기타
            Skill("조롱", 1, 3, 1, 2, taunt, power=1.0),

        # 레어 등급 (2)
            
            #공격
            Skill("강타", 1, 3, 2, 5, fixed_damage, power=50.0),
            Skill("분쇄", 1, 5, 2, 8, pulverize, power=2.0),
            Skill("저돌적 돌진", 1, 2, 2, 2, advance_damage, power=1.5),
            Skill("칼날의 춤", 1, 3, 2, 3, flurry, power=0.9),
            Skill("이중 공격", 1, 3, 2, 4, flurry, power=1.0),
            
            #피흡
            Skill("생명 갈취", 1, 1, 2, 5, life_steal, power=1.3),
            Skill("흡혈", 1, 3, 2, 3, drain_life, power=1.3),

            #지속피해
            Skill("과다출혈", 1, 3, 2, 10, exsanguinate, power=1.0),
            Skill("불구 만들기", 1, 2, 2, 2, cripple, power=-0.5),
            #효과
            Skill("광기", 1, 2, 2, 2, war_cry, power=30),
            Skill("사술", 1, 2, 2, 3, hex, power=1.0),
            Skill("약점 노출", 1, 2, 2, 1, hex, power=1.0),
            #Skill("침묵의 인장", 1, 2, 2, 2, silence, power=2),
            #Skill("무모한 분노", 1, 2, 2, 2, reckless_abandon, power=3),
            #Skill("거울 환영", 1, 2, 2, 2, mirror_image, power=2),
            #Skill("치명타", 1, 2, 2, 3, fatal_blow, power=1.8),

        # 영웅 등급 (3)

            Skill("처단", 1, 1, 3, 3, execute, power=2.5),
            Skill("방패 파괴", 1, 1, 3, 5, stun, power=2.0),
            Skill("그림자 형상", 1, 1, 3, 1, shadow, power=2.0),
            Skill("파멸의 파동", 1, 1, 3, 5, damage, power=2.3),
            Skill("영혼의 복수", 1, 1, 10, 10, reaping, power=1.2),
            Skill("영혼 파괴", 1, 1, 3, 1, pulverize, power=4.0),
            Skill("그림자 암살", 1, 1, 3, 2, flurry, power=1.5),

            Skill("약자멸시", 1, 1, 3, 5, scorn_the_weak, power=1.0),
            Skill("영혼 갈취", 1, 1, 3, 5, life_steal, power=2.5), # 피흡
            Skill("전장의 군주", 1, 1, 3, 10, war_cry, power=50),
            Skill("최후의 발악", 1, 1, 3, 1, iron_will, power=100.0),

            Skill("정화", 1, 1, 3, 1, lambda c, t, s: c.status_effects.clear(), power=1.0),
            Skill("어둠의 가호", 1, 1, 3, 1, bone_armor, power=40),
            
            Skill("피의 폭풍", 1, 1, 3, 2, exsanguinate, power=0.15),
            Skill("무력화의 저주", 1, 1, 3, 2, weaken, power=-0.3),
            Skill("실명의 빛", 1, 1, 3, 2, stun, power=1),
            Skill("초월적인 존재", 1, 1, 3, 1, shadow, power=1),

        # 전설 등급 (4)

            Skill("유성우", 1, 1, 4, 3, advance_damage, power=5.0),
            Skill("대지 가르기", 1, 10, 4, 10, advance_damage, power=1.2),
            Skill("세계의 종말", 1, 1, 4, 1, advance_damage, power=6.0),
            Skill("심판", 1, 4, 4, 10, execute, power=3.0),
            Skill("파멸의 일격", 1, 1, 4, 1, pulverize, power=10.0),

            #피흡
            Skill("영혼 포식", 1, 1, 4, 1, life_steal, power=4.0),
            Skill("철옹성", 1, 1, 4, 1, iron_will, power=30.0),
            Skill("태초 복구", 1, 1, 4, 3, heal, power=100.0), # 체력 전부 회복

            Skill("광전사의 격노", 1, 1, 4, 1, frenzy, power=0.5),
            Skill("불멸", 1, 1, 4, 1, shadow, power=4),
            
            Skill("고대의 외침", 1, 1, 4, 1, war_cry, power=10),
            Skill("신벌", 1, 5, 4, 2, execute, power=3.5),
            Skill("차원 붕괴", 1, 1, 4, 1, pulverize, power=3.2),
            Skill("아마겟돈", 1, 1, 4, 1, advance_damage, power=3.5),
            Skill("절대자의 권능", 1, 1, 4, 1, frenzy, power=0.6),



        # 몬스터 전용
            Skill("사라지기", 1, 1, 5, 2, shadow, power=2.0,is_monster_only=True),
            Skill("뼈 부수기", 1, 1, 5, 2, shatter_bone, power=1.0,is_monster_only=True),
            Skill("부패의 손길", 1, 1, 5, 99, weaken, power=-0.3,is_monster_only=True),
            Skill("대지 분쇄", 1, 1, 5, 2, advance_damage, power=2.0,is_monster_only=True),
            Skill("역병의 숨결", 1, 1, 5, 5, blight, power=0.07,is_monster_only=True),
            Skill("시간 왜곡", 1, 1, 5, 99, lambda c, t, s: print("시간의 흐름이 뒤틀린다."),is_monster_only=True),
            Skill("전염병", 1, 1, 5, 99, pestilence, is_monster_only=True, power=5),
            Skill("석화의 시선", 1, 1, 5, 99, petrifying_gaze, is_monster_only=True, power=1),
            Skill("영혼 흡수 오라", 1, 1, 5, 99, soul_drain_aura, is_monster_only=True, power=0.8),
            Skill("혐오체 소환", 1, 1, 5, 99, summon_abomination, is_monster_only=True, power=99),
            Skill("죽음의 손아귀", 1, 1, 5, 99, execute, is_monster_only=True, power=1.5),
            Skill("공포의 눈빛", 1, 1, 5, 99, weaken, is_monster_only=True, power=-0.4),
            Skill("부패시키는 저주", 1, 1, 5, 99, exsanguinate, is_monster_only=True, power=0.2),
            Skill("지옥불 폭풍", 1, 1, 5, 99, advance_damage, is_monster_only=True, power=2.8),
            Skill("영혼의 절규", 1, 1, 5, 99, silence, is_monster_only=True, power=2),
            Skill("포식", 1, 1, 5, 99, devour, is_monster_only=True, power=3.0),
            Skill("화염 숨결", 1, 1, 5, 99, fire_breath, is_monster_only=True, power=2.0),
            Skill("빙결 숨결", 1, 1, 5, 99, frost_breath, is_monster_only=True, power=1),
            Skill("독액 분출", 1, 1, 5, 99, poison_breath, is_monster_only=True, power=3),
            Skill("소용돌이", 1, 1, 5, 99, whirlpool, is_monster_only=True, power=2),
            Skill("영겁의 나락", 1, 1, 4, 99, stun, power=2.0,is_monster_only=True),
            Skill("존재 소각", 1, 1, 4, 99, execute, power=3.0,is_monster_only=True),
        ]
        self.all_skills_map = {skill.name: skill for skill in self.all_skills}

    def _initialize_equipment(self):
        self.all_equipment.extend([
            Equipment("튼튼한 나무 검", "무기", 2, attack=5, price=10),
            Equipment("녹슨 숏소드", "무기", 2, attack=10, price=15),
            Equipment("녹슨 냄비 뚜껑", "무기", 2, attack=2, defense=8, price=20),

            Equipment("부서진 도끼", "무기", 3, attack=14, price=37),
            Equipment("부식된 단검", "무기", 3, attack=10, critical=1000, price=37),
            Equipment("녹슨 식칼", "무기", 3, attack=10, critical=2000,price=42),

            Equipment("강철 브로드소드", "무기", 4, attack=20, price=80),
            Equipment("양날 도끼", "무기", 4, attack=25, price=87),
            Equipment("전사의 대검", "무기", 4, attack=30, price=105),
            Equipment("해골 파쇄기", "무기", 4, health=50, attack=20, price=125),
            Equipment("전투용 철퇴", "무기", 4, attack=27, defense=8, critical=10 ,price=130),
            Equipment("전사의 방패", "무기", 4, attack=5, defense=17, price=95),
            Equipment("전투로 닳고 닳은 창", "무기", 4, attack=20, critical=20, price=210),

            Equipment("피에 굶주린 전투도끼", "무기", 5, attack=40, price=370),
            Equipment("룬이 새겨진 클레이모어", "무기", 5, attack=60, defense=5, price=400),
            Equipment("암흑 기사의 롱소드", "무기", 5, attack=80, price=490),
            Equipment("피의 서약 대검", "무기", 5, attack=50, defense=-10, price=180),
            Equipment("수호자의 철퇴", "무기", 5, attack=16, defense=10, price=160),

            Equipment("용의 송곳니", "무기", 6, attack=22, health=20, price=300),
            Equipment("용의 비늘 도끼", "무기", 6, attack=20, health=150,price=350),


            Equipment("용뼈 망치", "무기", 8, attack=25, health=100, price=200),
            Equipment("신성 모독의 검", "무기", 8, attack=100, health=30, price=250),
        ])
        self.all_equipment.extend([
            Equipment("해진 가죽 흉갑", "흉갑", 1, defense=4, price=10),
            Equipment("녹슨 사슬 흉갑", "흉갑", 2, defense=8, price=30),
            Equipment("찌그러진 판금 흉갑", "흉갑", 4, defense=18, price=80),
            Equipment("용비늘 흉갑", "흉갑", 8, defense=30, health=30, price=200),
            Equipment("강철 흉갑", "흉갑", 1, defense=5, health=5, price=15),
            Equipment("가시 박힌 타워 흉갑", "흉갑", 5, defense=12, health=20, price=150),
            Equipment("암흑 기사의 흉갑", "흉갑", 3, defense=10, price=50),
            Equipment("피의 흉갑", "흉갑", 7, defense=22, price=180),
            Equipment("영웅의 유해 흉갑", "흉갑", 8, defense=20, health=15, price=160),
            Equipment("신성 모독의 흉갑", "흉갑", 9, defense=50, health=500, price=5000),
        ])
        self.all_equipment.extend([
            Equipment("가죽 투구", "투구", 1, defense=2, price=5),
            Equipment("철 투구", "투구", 2, defense=4, price=15),
            Equipment("강철 투구", "투구", 4, defense=8, price=30),
            Equipment("가죽 각반", "각반", 1, defense=2, price=5),
            Equipment("철 각반", "각반", 2, defense=4, price=15),
            Equipment("강철 각반", "각반", 4, defense=8, price=30),
        ])
        self.all_equipment.extend([
            Equipment("해골 장신구", "장신구", 1, health=10, attack=2, defense=2, price=20),
            Equipment("힘줄 장신구", "장신구", 3, attack=7, price=50),
            Equipment("생명의 돌 장신구", "장신구", 3, health=25, price=50),
            Equipment("뼈 부적 장신구", "장신구", 3, defense=7, price=50),
            Equipment("전투광의 장신구", "장신구", 6, health=20, attack=8, defense=8, price=150),
            Equipment("용맹의 징표", "장신구", 8, attack=12, health=25, price=220),
            Equipment("광전사의 표식", "장신구", 5, attack=10, price=120),
            Equipment("불굴의 맹세", "장신구", 7, attack=15, defense=-5, price=170),
            Equipment("수호자의 유물", "장신구", 9, defense=18, health=35, price=240),
            Equipment("왕의 해골 장신구", "장신구", 9, health=60, attack=18, defense=12, price=400),
        ])
    def _initialize_monsters(self):
        self.all_monsters.extend([
            Monster("부패한 수액괴물", 1, False, 20, 5, 2, 10, 10, 5, [self.get_skill("부패의 손길")]),
            Monster("비웃는 임프", 1, False, 25, 7, 3, 10, 10, 7, [self.get_skill("꿰뚫기")]),
            Monster("역병 쥐", 1, False, 15, 6, 1, 20, 10, 4, [self.get_skill("약화")]),
            Monster("흡혈박쥐", 1, False, 18, 5, 2, 30, 10, 5, [self.get_skill("생명 흡수")]),
            Monster("동굴 어둠살이", 1, False, 22, 6, 3, 10, 10, 6, [self.get_skill("기습")]),
            Monster("그림자 임프 군주", 1, True, 80, 12, 5, 10, 20, 50, [self.get_skill("꿰뚫기"), self.get_skill("사라지기")]),
        ])
        self.all_monsters.extend([
            Monster("광포한 오크", 2, False, 50, 10, 5, 10, 10, 10, [self.get_skill("분쇄")]),
            Monster("전쟁광 홉고블린", 2, False, 50, 12, 6, 10, 10, 12, [self.get_skill("전쟁의 포효")]),
            Monster("썩어가는 놀", 2, False, 50, 11, 4, 20, 10, 11, [self.get_skill("부패의 손길")]),
            Monster("굶주린 늑대", 2, False, 60, 13, 3, 30, 10, 10, [self.get_skill("과다출혈")]),
            Monster("해골 병사", 2, False, 50, 10, 8, 10, 10, 13, [self.get_skill("뼈 부수기")]),
            Monster("오크 전쟁군주", 2, True, 150, 15, 8, 10, 20, 100, [self.get_skill("분쇄"), self.get_skill("전쟁의 포효")]),
        ])
        self.all_monsters.extend([
            Monster("걸어다니는 시체", 3, False, 100, 15, 8, 10, 10, 15, [self.get_skill("생명 갈취")]),
            Monster("시체 포식자 구울", 3, False, 120, 17, 6, 10, 10, 17, [self.get_skill("포식")]),
            Monster("울부짖는 와이트", 3, False, 100, 16, 5, 20, 10, 16, [self.get_skill("영혼의 절규")]),
            Monster("돌가죽 가고일", 3, False, 120, 14, 10, 10, 10, 18, [self.get_skill("석화의 시선")]),
            Monster("탐욕의 미믹", 3, False, 110, 18, 12, 5, 20, 25, [self.get_skill("기절시키기")]),
            Monster("고대 리치", 3, True, 200, 25, 15, 10, 20, 150, [self.get_skill("죽음의 손아귀"), self.get_skill("뼈 갑옷"), self.get_skill("침묵의 인장")]),
        ])
        self.all_monsters.extend([
            Monster("미궁의 미노타우르스", 4, False, 150, 22, 10, 10, 15, 39, [self.get_skill("저돌적 돌진")]),
            Monster("비명지르는 하피", 4, False, 120, 20, 8, 30, 10, 30, [self.get_skill("영혼의 절규")]),
            Monster("복수심에 불타는 켄타우로스", 130, False, 70, 25, 9, 20, 10, 50, [self.get_skill("칼날의 춤")]),
            Monster("폭풍의 그리폰", 4, False, 140, 24, 12, 15, 10, 26, [self.get_skill("실명의 빛")]),
            Monster("외눈의 사이클롭스", 4, False, 125, 28, 15, 5, 10, 30, [self.get_skill("대지 분쇄")]),
            Monster("석화의 메두사", 4, True, 157, 35, 18, 20, 25, 250, [self.get_skill("석화의 시선"), self.get_skill("독액 분출")]),
        ])
        self.all_monsters.extend([
            Monster("흑요석 골렘", 5, False, 180, 30, 20, 0, 10, 185, [self.get_skill("강철의 의지")]),
            Monster("독액의 와이번", 5, False, 190, 35, 15, 20, 15, 216, [self.get_skill("역병의 숨결")]),
            Monster("죽음의 시선 바실리스크", 5, False, 200, 32, 18, 10, 10, 170, [self.get_skill("석화의 시선")]),
            Monster("심연의 나가", 5, False, 210, 38, 16, 25, 15, 40, [self.get_skill("침묵의 인장")]),
            Monster("타락한 서큐버스", 5, False, 220, 40, 14, 30, 20, 45, [self.get_skill("생명 갈취")]),
            Monster("악몽의 키메라", 5, True, 400, 45, 25, 15, 30, 400, [self.get_skill("화염 숨결"), self.get_skill("독액 분출"), self.get_skill("빙결 숨결")]),
        ])
        self.all_monsters.extend([
            Monster("심해의 정령", 6, False, 270, 40, 25, 20, 10, 45, [self.get_skill("올가미")]),
            Monster("화염의 정령", 6, False, 250, 45, 22, 20, 15, 48, [self.get_skill("지옥불 폭풍")]),
            Monster("소용돌이의 정령", 6, False, 245, 42, 20, 30, 10, 46, [self.get_skill("칼날의 춤")]),
            Monster("대지의 정령", 6, False, 210, 38, 30, 10, 10, 50, [self.get_skill("대지 분쇄")]),
            Monster("그림자 암살자", 6, False, 200, 50, 18, 40, 25, 55, [self.get_skill("그림자 암살")]),
            Monster("심연의 히드라", 6, True, 550, 55, 30, 10, 20, 550, [self.get_skill("포식"), self.get_skill("독액 분출"), self.get_skill("저주")]),
        ])
        self.all_monsters.extend([
            Monster("지옥의 병사", 7, False, 320, 55, 30, 10, 15, 60, [self.get_skill("전쟁의 포효")]),
            Monster("비열한 임프", 7, False, 340, 52, 28, 25, 10, 58, [self.get_skill("사라지기")]),
            Monster("지옥견", 7, False, 370, 60, 25, 30, 15, 65, [self.get_skill("과다출혈")]),
            Monster("뼈의 용", 7, False, 400, 65, 40, 10, 20, 80, [self.get_skill("뼈 갑옷")]),
            Monster("타락한 천사", 7, False, 320, 70, 35, 20, 25, 90, [self.get_skill("신벌")]),
            Monster("거대한 베히모스", 7, True, 750, 70, 40, 5, 25, 700, [self.get_skill("대지 분쇄"), self.get_skill("철옹성")]),
        ])
        self.all_monsters.extend([
            Monster("서리 거인", 8, False, 510, 70, 40, 10, 15, 80, [self.get_skill("빙결 숨결")]),
            Monster("용암 거인", 8, False, 452, 75, 38, 10, 15, 85, [self.get_skill("화염 숨결")]),
            Monster("폭풍 거인", 8, False, 400, 72, 35, 20, 15, 82, [self.get_skill("실명의 빛")]),
            Monster("고대 용거북", 8, False, 460, 65, 60, 0, 10, 100, [self.get_skill("철옹성")]),
            Monster("죽음의 기사", 8, False, 600, 80, 50, 15, 20, 110, [self.get_skill("죽음의 손아귀")]),
            Monster("심해의 레비아탄", 8, True, 1000, 85, 50, 10, 30, 900, [self.get_skill("대지 가르기"), self.get_skill("소용돌이")]),
        ])
        self.all_monsters.extend([
            Monster("고위 악마", 9, False, 700, 85, 50, 15, 20, 120, [self.get_skill("지옥불 폭풍")]),
            Monster("심연의 감시자", 9, False, 720, 82, 48, 20, 20, 115, [self.get_skill("약점 노출")]),
            Monster("공허의 약탈자", 9, False, 680, 90, 45, 25, 20, 125, [self.get_skill("차원 붕괴")]),
            Monster("고대 정령", 9, False, 650, 80, 60, 10, 15, 140, [self.get_skill("정화의 불길")]),
            Monster("신화 속 야수", 9, False, 600, 95, 55, 10, 25, 150, [self.get_skill("태초의 광기")]),
            Monster("타락한 대천사", 9, True, 1300, 100, 60, 20, 35, 1200, [self.get_skill("신벌"), self.get_skill("처단"), self.get_skill("전염병")]),
        ])
        self.all_monsters.extend([
            Monster("고룡", 10, False, 1100, 100, 70, 10, 25, 200, [self.get_skill("화염 숨결")]),
            Monster("서리 고룡", 10, False, 900, 110, 65, 15, 25, 220, [self.get_skill("빙결 숨결")]),
            Monster("암흑 고룡", 10, False, 980, 120, 60, 20, 25, 250, [self.get_skill("역병의 숨결")]),
            Monster("분노의 고룡", 10, False, 890, 130, 80, 10, 30, 300, [self.get_skill("광전사의 격노")]),
            Monster("황금 고룡", 10, False, 857, 110, 90, 10, 20, 1000, [self.get_skill("신의 가호")]),
            Monster("심연의 끝", 10, True, 2000, 150, 80, 20, 50, 0, [self.get_skill("존재 소각"), self.get_skill("영겁의 나락"), self.get_skill("지옥불 폭풍")]),
        ])

    def get_skill(self, name):
        skill_template = self.all_skills_map.get(name)
        if skill_template:
            return Skill(skill_template.name, skill_template.level, skill_template.max_level, skill_template.rarity, skill_template.initial_use_count, skill_template.effect, skill_template.is_monster_only)
        return None

    def start(self):
        print("...어둠 속에서 희미한 의식이 깨어난다...\n")
        time.sleep(2)
        print("심연의 깊은 구멍 속 종소리가 메아리친다...\n")
        time.sleep(2)
        print("너는 부름을 받았다. 움직이자.")
        time.sleep(2)
        while self.player.is_alive() and self.stage <= 10:
            self.progress_stage()
        if self.player.is_alive():
            print("너의 발자취는 피로 쓰였고, 이곳엔 아무것도 남아있지 않다")
            time.sleep(2)
            print("끈질긴 생명이다. 하지만 이 저주받은 땅에서 네놈의 공허한 여정은 끝나지 않았다.\n")
            time.sleep(2)
            print("Thanks for playing :3")
            input()
        else:
            print("결국, 너의 영혼도 이 땅의 일부가 되었다.\n")
            input()

    def progress_stage(self):
        print(f"\n--------- 제 {self.stage} 장 ---------\n")
        if self.stage == 1:
            print("           깨어난 곳         ")
            print("-----------------------------"); time.sleep(1.5)
            print("어둠 속에서 길을 찾는다...\n"); time.sleep(1.5)
            print("동굴의 음습함은 너를 기분 좋게 만들었다.\n"); time.sleep(1.5)
            print("하지만, 이곳은 결코 안전하지 않다.\n"); time.sleep(1.5)
        if self.stage == 2:
            print("             깊은 동굴         ")
            print("-----------------------------"); time.sleep(1.5)
            print("깊은 동굴 속, 차가운 공기가 피부를 스친다.\n"); time.sleep(1.5)
            print("어둠 속에서 무언가가 너를 지켜보고 있다...\n"); time.sleep(1.5)
            print("긴장감을 늦추지 말아야 한다.\n"); time.sleep(1.5)
        if self.stage == 3:
            print("             물 웅덩이         ")
            print("-----------------------------"); time.sleep(1.5)
            print("동굴의 벽이 점점 좁아진다...\n"); time.sleep(1.5)
            print("발밑에서 물방울이 떨어지는 소리가 메아리친다.\n"); time.sleep(1.5)
            print("너는 물 웅덩이를 힘껏 즈려밟는다.\n"); time.sleep(1.5)
        if self.stage == 4:
            print("             심연의 소리        ")
            print("-----------------------------"); time.sleep(1.5)
            print("어둠 속에서 무언가가 꿈틀거린다...\n"); time.sleep(1.5)
            print("숨을 죽이고, 귀를 기울인다...\n"); time.sleep(1.5)
            print("너는 이곳에서 살아남아야 한다.\n"); time.sleep(1.5)
        if self.stage == 5:
            print("             빛의 흔적         ")
            print("-----------------------------"); time.sleep(1.5)
            print("동굴의 벽이 빛을 반사한다...\n"); time.sleep(1.5)
            print("희미한 빛줄기가 너의 길을 비춘다...\n"); time.sleep(1.5)
            print("너는 이 빛을 따라가야 한다.\n"); time.sleep(1.5)
        if self.stage == 6:
            print("             차가운 바람        ")
            print("-----------------------------"); time.sleep(1.5)
            print("차가운 바람이 동굴 속을 휘감는다...\n"); time.sleep(1.5)
            print("너는 이 바람 속에서 무언가를 느낀다...\n"); time.sleep(1.5)
            print("이 바람은 너를 시험에 들게 할 것이다.\n"); time.sleep(1.5)
        if self.stage == 7:
            print("             거친 벽          ")
            print("-----------------------------"); time.sleep(1.5)
            print("동굴의 벽이 점점 더 거칠어진다...\n"); time.sleep(1.5)
            print("너는 이 거친 벽을 지나야 한다...\n"); time.sleep(1.5)
            print("너는 이곳에서 길을 잃지 말아야 한다.\n"); time.sleep(1.5)
        if self.stage == 8:
            print("             속삭이는 어둠       ")
            print("-----------------------------"); time.sleep(1.5)
            print("어둠 속에서 무언가가 속삭인다...\n"); time.sleep(1.5)
            print("너는 이 속삭임에 귀를 기울인다...\n"); time.sleep(1.5)
            print("이 속삭임은 너를 미치게 할 것이다.\n"); time.sleep(1.5)
        if self.stage == 9:
            print("             빛 속의 그림자         ")
            print("-----------------------------"); time.sleep(1.5)
            print("동굴의 벽이 점점 더 빛난다...\n"); time.sleep(1.5)
            print("너는 이 빛 속에서 무언가를 본다...\n"); time.sleep(1.5)
            print("끝이 다가오고 있다는것을 직감한다.\n"); time.sleep(1.5)
        if self.stage == 10:
            print("             심연의 끝         ")
            print("-----------------------------"); time.sleep(1.5)
            print("어둠 속에서 무언가가 울부짖는다...\n"); time.sleep(1.5)
            print("너는 이 울부짖음에 귀를 기울인다...\n"); time.sleep(1.5)
            print("마지막이 되리란 예감이 든다.\n"); time.sleep(1.5)
        print("- 한발짝 더 나아간다... -\n")
        time.sleep(2)
        self.battle_count = 0
        while self.battle_count < 3:
            self.battle_count += 1
            print(f"\n--- 피비린내 나는 전투 {self.battle_count}/3 ---")
            monster = self.get_random_monster(self.stage, is_boss=False)
            if not self.battle(monster):
                return
        time.sleep(1)
        boss = self.get_random_monster(self.stage, is_boss=True)
        if self.battle(boss):
            self.player.heal(self.player.max_health)
            self.stage += 1
            self.shop()
        else:
            return

    def get_random_monster(self, stage, is_boss):
        monster_pool = [m for m in self.all_monsters if m.stage == stage and m.is_boss == is_boss]
        monster_template = random.choice(monster_pool) if monster_pool else None
        if not monster_template:
            return None
        monster = Monster(monster_template.name, monster_template.stage, monster_template.is_boss, 
                          monster_template.max_health, monster_template.attack, monster_template.defense, 
                          monster_template.evasion, monster_template.critical, monster_template.gold, monster_template.skills)
        
        return monster

    def battle(self, monster):
        print(f"\n{monster.name}이(가) 모습을 드러냈다.\n")
        time.sleep(1)
        monster.show_stats()
        time.sleep(1)
        while self.player.is_alive() and monster.is_alive():
            for character in [self.player, monster]:
                for effect in character.status_effects[:]:
                    effect.apply_effect(character)
                    effect.duration -= 1
                    if effect.duration <= 0:
                        character.status_effects.remove(effect)
                        print(f"{character.name}의 {effect.name} 효과가 사라졌다.\n")

            if not monster.is_alive(): break

            self.player_turn(monster)
            if not monster.is_alive(): break

            self.monster_turn(monster)
            if not self.player.is_alive(): break

        if self.player.is_alive():
            print(f"\n{monster.name}의 시체를 넘고 전진한다.\n")
            time.sleep(1)
            self.player.gold += monster.gold
            print(f"{monster.gold}G의 피 묻은 금화를 챙겼다. (현재 소지량: {self.player.gold}G)\n")
            time.sleep(1)
            self.battle_reward(is_boss=monster.is_boss)
            return True
        else:
            print(f"\n{self.player.name}은(는) 결국 쓰러졌다...\n")
            time.sleep(1)
            return False

    def player_turn(self, monster):
        self.player.show_stats()
        print("1. 휘두르기 Lv.1 (*)")
        for i, skill in enumerate(self.player.skills):
            print(f"{i+2}. {skill.name} Lv.{skill.level} ({skill.use_count}/{skill.initial_use_count})")
        while True:
            try:
                choice = int(input("행동을 선택하자: "))
                if 1 <= choice <= len(self.player.skills) + 1:
                    break
                else:
                    print("어둠 속에서 길을 잃었는가? 다시 선택하라.")
            except ValueError:
                print("알 수 없는 속삭임이다. 명확한 답을 내놓아라.")

        if choice == 1:
            #self.player.deal_physical_damage(monster, self.player.attack)
            self.player.deal_damage(monster, self.player.attack)
        else:
            skill = self.player.skills[choice-2]
            skill.execute(self.player, monster)
            if skill.use_count <= 0:
                self.player.skills.remove(skill)
                print(f"{skill.name}의 힘을 모두 소진했다.\n")
        time.sleep(1.5)

    def monster_turn(self, monster_obj):
        if monster_obj.skills and random.random() < 0.3:
            skill = random.choice(monster_obj.skills)
            print(f"{monster_obj.name}이(가) {skill.name}을(를) 사용한다.")
            skill.execute(monster_obj, self.player)
        else:
            print(f"{monster_obj.name}의 공격.")
            monster_obj.deal_damage(self.player, monster_obj.attack)
        time.sleep(1.5)

    def battle_reward(self, is_boss):
        print("\n--- 적을 무로 돌렸다 ---")
        time.sleep(2)
        heal_amount = round(self.player.max_health * 0.3)
        self.player.heal(heal_amount)
    
        print("너는 이 전투에서 무엇을 얻었는가:\n")
        time.sleep(1.5)
    
        health_increase = 10 + (self.stage * 2)
        attack_increase = 3 + (self.stage // 2)
        defense_increase = 2 + (self.stage // 3)
        crit_increase = 2
    
        choices_data = [
            ("육체 강화", "max_health", health_increase, "생명"),
            ("힘줄 강화", "attack", attack_increase, "공격")
        ]
        if self.stage >= 3:
            choices_data.append(("골격 강화", "defense", defense_increase, "방어"))
            choices_data.append(("예리함 연마", "critical", crit_increase, "강타"))
    
        for i, (name, stat_key, value, unit_text) in enumerate(choices_data):
            if stat_key == "critical":
                print(f"{i+1}. {name} (+{value:.1f}% {unit_text})\n")
            else:
                print(f"{i+1}. {name} (+{value} {unit_text})\n")
            time.sleep(0.5)
    
        while True:
            try:
                prompt = f"선택의 시간이다. (1-{len(choices_data)}): "
                choice = int(input(prompt))
                if 1 <= choice <= len(choices_data):
                    chosen_name, stat_key, value, _ = choices_data[choice - 1]
                    if stat_key == "max_health":
                        self.player.max_health += value
                        self.player.current_health += value
                        print(f"{chosen_name}으로 생명력이 {value}만큼 증가했다.\n")
                    elif stat_key == "attack":
                        self.player._base_attack += value
                        self.player.attack += value
                        print(f"{chosen_name}으로 공격력이 {value}만큼 증가했다.\n")
                    elif stat_key == "defense":
                        self.player._base_defense += value
                        self.player.defense += value
                        print(f"{chosen_name}으로 방어력이 {value}만큼 증가했다.\n")
                    elif stat_key == "critical":
                        self.player.critical += value
                        print(f"{chosen_name}으로 강타가 {value}만큼 증가했다.\n")
                    break
                else:
                    print("어둠 속에서 길을 잃었는가? 다시 선택하라.")
            except ValueError:
                print("알 수 없는 속삭임이다. 명확한 답을 내놓아라.")
        time.sleep(1)
    
        self.skill_acquisition(is_boss)

    def skill_acquisition(self, is_boss):
        print("\n어둠 속에서 새로운 힘이 느껴진다...\n")
        time.sleep(1)

        potential_skills_to_offer = [s for s in self.all_skills if s.level < s.max_level and not s.is_monster_only]

        player_unmaxed_skills = [s for s in self.player.skills if s.level < s.max_level]

        choices = []


        if player_unmaxed_skills:
            guaranteed_skill = random.choice(player_unmaxed_skills)
            choices.append(guaranteed_skill)

            potential_skills_to_offer = [s for s in potential_skills_to_offer if s.name != guaranteed_skill.name]

        remaining_slots = 3 - len(choices)

        if remaining_slots > 0:
            if is_boss:
                high_rarity_skills = [s for s in potential_skills_to_offer if s.rarity >= 3]
                low_rarity_skills = [s for s in potential_skills_to_offer if s.rarity < 3]

                if high_rarity_skills:
                    choices.extend(random.sample(high_rarity_skills, min(remaining_slots, len(high_rarity_skills))))
                    remaining_slots = 3 - len(choices)

                if remaining_slots > 0 and low_rarity_skills:
                    choices.extend(random.sample(low_rarity_skills, min(remaining_slots, len(low_rarity_skills))))

            else: # 보스가 아닐때
                if potential_skills_to_offer:

                    weights = [10 / s.rarity for s in potential_skills_to_offer]

                    num_to_pick = min(remaining_slots, len(potential_skills_to_offer))
                    choices.extend(random.choices(potential_skills_to_offer, weights=weights, k=num_to_pick))
    
        unique_choices = []
        seen_names = set()
        for skill in choices:
            if skill.name not in seen_names:
                unique_choices.append(skill)
                seen_names.add(skill.name)
        choices = unique_choices
        
        if not choices:
            print("더 이상 얻을 수 있는 힘이 없다.\n")
            time.sleep(1)
            return

        print("어떤 힘을 받아들이겠는가, 가진 힘을 고르면 해당 힘이 더욱 강해진다:\n")
        time.sleep(1)
        for i, skill in enumerate(choices):
            current_level = next((s.level for s in self.player.skills if s.name == skill.name), 0)
            print(f"{i+1}. {skill.name} (시전 가능 횟수: {skill.use_count}, 희귀도: {skill.rarity}, 레벨: {current_level}/{skill.max_level}\n")
        print(f"{len(choices)+1}. 이 힘을 거부한다.\n")

        while True:
            try:
                choice = int(input("어떤 힘을 받아들이겠는가?: "))
                if 1 <= choice <= len(choices):
                    chosen_skill = choices[choice-1]
                    self.add_or_level_up_skill(chosen_skill)
                    break
                elif choice == len(choices) + 1:
                    print("힘을 거부했다.\n")
                    break
                else:
                    print("어둠 속에서 길을 잃었는가? 다시 선택하라.")
            except ValueError:
                print("알 수 없는 속삭임이다. 명확한 답을 내놓아라.")

    def player_has_skill(self, skill_name):
        return any(s.name == skill_name for s in self.player.skills)

    def add_or_level_up_skill(self, skill_to_add):
        for skill in self.player.skills:
            if skill.name == skill_to_add.name:
                skill.level += 1
                skill.reset_use_count()
                print(f"{skill.name}이(가) 더욱 강해졌다. Lv.{skill.level}\n")
                return
        if len(self.player.skills) >= 4:
            print("영혼의 그릇은 가득 찼다. 새로운 힘을 담으려면, 낡은 것을 비워야 할 것이다.")
            for i, skill in enumerate(self.player.skills):
                print(f"{i+1}. {skill.name} (Lv.{skill.level})")
            print(f"{len(self.player.skills)+1}. 거부한다.")
            
            while True:
                try:
                    choice = int(input("어떤 힘을 버리고 새로운 힘을 받아들이겠는가? "))
                    if 1 <= choice <= len(self.player.skills):
                        forgotten_skill = self.player.skills.pop(choice - 1)
                        print(f"힘 '{forgotten_skill.name}'은(는) 기억 속에서 희미해졌다.")
                        new_skill = self.get_skill(skill_to_add.name)
                        self.player.skills.append(new_skill)
                        print(f"새로운 힘 '{new_skill.name}'이(가) 영혼에 각인되었다!\n")
                        break
                    elif choice == len(self.player.skills) + 1:
                        print("새로운 힘을 거부하고, 익숙한 그림자에 머물렀다.\n")
                        break
                    else:
                        print("어둠 속에서 길을 잃었는가? 다시 선택하라.")
                except ValueError:
                    print("알 수 없는 속삭임이다. 명확한 답을 내놓아라.")
        else:
            new_skill = self.get_skill(skill_to_add.name)
            self.player.skills.append(new_skill)
            print(f"새로운 힘 '{new_skill.name}'을(를) 얻었다.\n")

    def shop(self):
        print("\n[ 수상한 상점 ]")
        time.sleep(1)
        print("필요한 게 있나, 이방인...?\n")
        time.sleep(1)
        self.player.show_stats()
        self.player.show_inv()
        time.sleep(1)
        available_items = [item for item in self.all_equipment if item.stage <= self.stage]
        shop_inventory = random.sample(available_items, min(5, len(available_items)))

        while True:
            print(f"\n[피 묻은 금화: {self.player.gold}G]\n")
            for i, item in enumerate(shop_inventory):
                stats_display = []
                if item.health != 0:
                    stats_display.append(f"생명: {item.health}")
                if item.attack != 0:
                    stats_display.append(f"공격: {item.attack}")
                if item.defense != 0:
                    stats_display.append(f"방어: {item.defense}")
                if item.critical != 0:
                    stats_display.append(f"강타: {item.critical}")
                if item.evasion != 0:
                    stats_display.append(f"민첩: {item.evasion}")
                
                stats_str = ", ".join(stats_display)
                
                print(f"{i+1}. {item.name} ({item.part}) - {item.price}G ({stats_str})")
            print(f"{len(shop_inventory)+1}. 떠난다\n")

            while True:
                try:
                    choice = int(input("선택의 시간이다. :"))
                    if 1 <= choice <= len(shop_inventory) + 1:
                        break
                    else:
                        print("어둠 속에서 길을 잃었는가? 다시 선택하라.")
                except ValueError:
                    print("알 수 없는 속삭임이다. 명확한 답을 내놓아라.")

            if choice == len(shop_inventory) + 1:
                print("상점 주인이 어둠 속으로 사라진다.\n")
                break
            else:
                chosen_item = shop_inventory[choice-1]
                if self.player.gold >= chosen_item.price:
                    self.player.gold -= chosen_item.price
                    self.player.equip(chosen_item)
                    shop_inventory.pop(choice-1)
                else:
                    print("금화가 부족하다.")
            time.sleep(2)


if __name__ == "__main__":
    print(i_was_bored)
    if input() == "help":
        print(help_text)
        input()
    game = Game()
    game.start()
