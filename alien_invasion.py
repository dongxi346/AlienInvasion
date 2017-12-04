import sys
import pygame
import game_functions as gf


from settings import Settings
from ship import Ship
from alien import Alien
from pygame.sprite import Group
from game_stats import GameStats


def run_game():
    # 初始化游戏并创建屏幕对象
    pygame.init()
    ai_settings = Settings() ;
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))

    pygame.display.set_caption("Alien Invasion")

    # 在屏幕上创建飞船
    ship = Ship(ai_settings, screen)

    # 将子弹存储在一个编组中
    bullets = Group()
    # 将外星人存储在一个编组中
    aliens = Group()

    # 创建外星人群
    gf.create_fleet(ai_settings,screen,ship,aliens)

    # 设置背景色
    bg_color = (ai_settings.bg_color)

    # 创建一个外星人实例
    alien = Alien(ai_settings, screen)

    # 创建一个用于存储游戏统计的实例
    stats = GameStats(ai_settings)

    # 开始游戏的主要循环
    while True:
        # 监听键盘和鼠标事件
        gf.check_events(ai_settings, screen, ship, bullets)

        if stats.game_active:
            # 刷新飞船的位置
            ship.update()
            # 更新子弹的位置
            gf.update_bullets(ai_settings, screen, ship, aliens, bullets)

            # 更新外星人的位置
            gf.update_aliens(ai_settings, stats, screen, ship, aliens, bullets)

        # 刷新屏幕
        gf.update_screen(ai_settings, screen, ship, aliens, bullets)

run_game()
