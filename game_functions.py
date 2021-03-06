import sys
import pygame

from bullet import Bullet
from alien import Alien
from time import sleep

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 按下q 退出游戏
            write_high_score(stats)
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    """玩家单击开始按钮开始游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # 重置游戏设置
        ai_settings.initialize_dynamic_settings()
        # 隐藏光标
        pygame.mouse.set_visible(False)
        # 重置游戏统计信息
        stats.reset_stats()
        stats.game_active = True

        # 重置记分牌图像
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并让飞船居中
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

def check_keydown_events(event, ai_settings, screen, stats, ship, bullets):
    # 响应鼠标按下事件
    if event.key == pygame.K_RIGHT:
        # 按下向右移动飞船
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        # 按下向左移动飞船
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        # 创建一颗子弹，并将其加入到编组bullets中, 控制只能发射3颗子弹
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        # 按下q退出游戏
        write_high_score(stats)
        sys.exit()

def write_high_score(stats):
    # 先读取文件，如果最高分比文件中的分数还低就不写入文件，否则写入文件
    read_high_score_txt = int(read_high_score())
    if read_high_score_txt < stats.high_score:
        write_file = 'high_score.txt'
        with open(write_file, 'w') as write_file_object:
            write_file_object.write(str(stats.high_score))

def read_high_score():
    """读取文件中的最高分"""
    read_file = 'high_score.txt'
    with open(read_file) as read_file_object:
        read_high_score = read_file_object.read()
    return read_high_score

def check_keyup_events(event, ship):
    # 响应鼠松开事件
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """更新子弹的位置，并删除已经消失的子弹"""
    bullets.update()
    # 删除消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # 响应子弹和外星人的碰撞
    # 删除发生碰撞的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens,True, True)

    # 统计击杀的外星人分数
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()

        check_high_score(stats, sb)

    if len(aliens) == 0:
        # 删除现有的子弹,加快游戏节奏，并新建一群外星人
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)

        # 如果整群外星人被消灭了，就提高一个等级
        stats.level += 1
        sb.prep_level()

def check_high_score(stats, sb):
        """检查是否诞生了新的最高分"""
        if stats.score > stats.high_score:
            stats.high_score = stats.score
            sb.prep_high_score()

def fire_bullet(ai_settings, screen, ship, bullets):
    """如果还没达到子弹的发射上限，就发射一颗子弹"""
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings,ship.rect.height, alien.rect.height)

    # 创建第一行外星人
    """
    for alien_number in range(number_aliens_x):
        # 创建一个外星人并将其加入当前行
        alien = Alien(ai_settings, screen)
        create_alien(ai_settings, screen, aliens, alien_number)
    """
    # 创建外星人群
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            # 创建一个外星人并将其加入当前行
            alien = Alien(ai_settings, screen)
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def get_number_aliens_x(ai_settings, alien_width):
    # 外星人间距为外星人的宽度 计算一行可容纳多少个外星人
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
    """计算屏幕可以容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    # 创建一个外星人
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width

    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def check_fleet_edges(ai_settings, aliens):
    """有外星人到达边缘时采取响应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """将整体外星人下移，并改变他们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """检查是否有外星人在屏幕边缘，并更新正群外星人的位置"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        print("Ship hit!!!")
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)

def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # 响应被外星人撞到的飞船
    if stats.ships_left > 0:

        # 将ship_left减1
        stats.ships_left -= 1

        # 更新飞船数
        sb.prep_ships()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并将飞创放到屏幕底部的中间
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # 暂停
        sleep(0.5)
    else:
        stats.game_active = False
        # 非游戏状态显示光标
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """检查是否有外星人到达屏幕底部"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样处理
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
            break

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """更新屏幕上的图像，并切换到新的屏幕"""
    # 每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color)
    # 在飞船和外星人后面重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    aliens.draw(screen)

    # 显示得分
    sb.show_score()

    # 如果游戏处于非活动状态，就绘制Play按钮
    if not stats.game_active:
        play_button.draw_botton()


    # 让最近绘制的屏幕可见
    pygame.display.flip()

