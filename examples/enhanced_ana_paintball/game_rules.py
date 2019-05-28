# Original by the one and only Jinko#2838
# https://workshop.elohell.gg/AbJBNOUW0
# Converted to Python by Peppermint#2241

each_player  = ongoing_each_player(all, all)
on_elim      = player_earned_elimination(all, all)
player_score = score_of(event_player)
is_scoping   = is_firing_secondary(event_player)
message      = string("{0}: {1}", string("current objective", null, null, null), string("{0} {1}", string("sleep", null, null, null), string("enemies", null, null, null), null), null)

rule "Gamemode by Jinko#2838 - Join the discord for the lastest code version! (use Google)":
	pass

rule "Map detector (credits: Kevlar)":
	pos = x_component_of(nearest_walkable_position(vector(100, 100, 100)))
	add_action(set(global_Z, round_to_integer(pos, up)))

rule "Disable built-in game ending":
	add_action(disable_built_in_game_mode_completion)

rule "Start match sooner":
	add_condition(is_assembling_heroes == true)
	
	add_action(
		wait(1, ignore_condition),
		set_match_time(10)
	)

rule "Random voice line when match starts":
	set_event(each_player)
	
	add_condition(
		has_spawned(event_player) == true,
		number_of_deaths(event_player) == 0
	)
	
	add_action(skip(2 * random_integer(0, 4)))
	for voice_line in [ voice_line_up, voice_line_right, voice_line_down, voice_line_left ]:
		add_action(
			communicate(event_player, voice_line),
			abort
		)

rule "If kills an enemy, says hello":
	set_event(on_elim)
	
	add_condition(is_alive(event_player) == true)
	
	add_action(
		skip_if(player_score >= 24, 1),
		communicate(event_player, hello)
	)

def hardscope_rule(effect):
	conditions = is_scoping == true
	
	text = string("{0} {1}", string("times", null, null, null), string("up", null, null, null), null)
	actions = [
		wait(1.7, abort_when_false),
		destroy_hud_text(player_variable(event_player, E)),
		set_status(event_player, null, effect, 1),
		create_hud_text(event_player, text, null, null, top, 100, red, white, white, visible_to_and_string),
		set_player_variable(event_player, F, last_text_id),
		wait(1, ignore_condition),
		destroy_hud_text(player_variable(event_player, F))
	]
	
	return conditions, actions

rule "If hardscopes (> 1,5 sec.), gets stunned 1 sec":
	set_event(each_player)
	
	add_condition(global_Z != 18)
	
	c, a = hardscope_rule(stunned)
	add_condition(c)
	add_action(a)

rule "If hardscopes (> 1,5 sec.), gets frozen 1 sec":
	set_event(each_player)
	
	add_condition(global_Z == 18)
	
	c, a = hardscope_rule(frozen)
	add_condition(c)
	add_action(a)

rule "Hardscope timer":
	set_event(each_player)
	
	add_condition(
		is_scoping == true,
		match_time <= 899
	)
	
	add_action(
		set(event_player.T, 1.5),
		chase_player_variable_at_rate(event_player, T, 0, 1, destination_and_rate),
		create_hud_text(event_player, event_player.T, null, null, top, 5, white, white, white, visible_to_and_string),
		set(event_player.E, last_text_id),
		wait(1.5, abort_when_false),
		destroy_hud_text(event_player.E)
	)

rule "Unscope = destroy hardscope timer":
	set_event(each_player)
	
	add_condition(is_scoping == false)
	
	add_action(destroy_hud_text(event_player.E))

rule "If score < 24, allow primary, allow secondary, disable ult":
	set_event(each_player)
	
	add_condition((player_score < 24) & is_alive(event_player) == true)
	
	add_action(
		set_ultimate_ability_enabled(event_player, false),
		allow_button(event_player, primary_fire),
		allow_button(event_player, secondary_fire)
	)

rule "If score > 19, apply burning effect":
	set_event(on_elim)
	
	add_condition(player_score > 19)
	
	add_action(set_status(event_player, null, burning, 9999))

rule "If score < 20, disable burning effect":
	set_event(each_player)
	
	add_condition(player_score < 20)
	
	add_action(clear_status(event_player, burning))

rule "If score = 24, nanoboost themselves, can only use sleep dart":
	set_event(on_elim)
	
	add_condition(player_score == 24)
	
	add_action(
		disallow_button(event_player, primary_fire),
		disallow_button(event_player, secondary_fire),
		
		set_ultimate_ability_enabled(event_player, true),
		set_ultimate_charge(event_player, 100),
		press_button(event_player, ultimate),
		
		big_message(event_player, message),
		wait(0.25, ignore_condition),
		set_ultimate_ability_enabled(event_player, false)
	)

rule "If score = 24 and died, nanoboost themselves":
	set_event(player_died(all, all))
	
	add_condition(player_score == 24)
	
	add_action(
		set_ultimate_ability_enabled(event_player, true),
		wait(2.1, ignore_condition),
		set_ultimate_charge(event_player, 100),
		press_button(event_player, ultimate),
		small_message(event_player, message)
	)
