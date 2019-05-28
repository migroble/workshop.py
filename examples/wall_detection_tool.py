# Original by mah man XxHARAMBExX
# https://workshop.elohell.gg/_muoBQxw8
# Converted to Python by Peppermint#2241

step = 20

rule "Range of detection":
	set_event(ongoing_each_player(all, all))
	
	add_action(
		set(event_player.R, 1),
		create_hud_text(all_players(team(all)),  event_player.S, null, null, left, 0, yellow, white, white, visible_to_and_string)
	)

eye_pos = eye_position(event_player)
def los_check(angle):
	return is_in_line_of_sight(eye_pos, eye_pos + direction_from_angles(angle,  0) * event_player.R, barriers_do_not_block_los)

rule "On wall":
	set_event(ongoing_each_player(all, all))
	
	los = los_check(0)
	for i in range(step, 360, step):
		los &= los_check(i)
	add_condition(los == false)
	
	add_action(
		set(event_player.S, 1),
		wait(0.016, restart_when_true),
		loop_if_condition_is_true,
		set(event_player.S, 0)
	)
