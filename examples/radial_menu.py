# Original by /u/Oran9eUtan
# https://redd.it/bq45gc
# Converted to Python by Peppermint#2241

each_player = ongoing_each_player(all, all)
n_allowed_heroes = count_of(allowed_heroes(event_player))
interact_pressed = is_button_held(event_player, interact)
eye_pos = eye_position(event_player)

rule "Reset menu positions (trigger: game start || num of allowed heroes changed)":
	set_event(each_player)
	
	add_condition(count_of(event_player.P) != n_allowed_heroes)
	
	add_action(set(event_player.P, empty_array))

def set_menu_position(position, angle):
	return set_at_index(event_player.P, position, vector(sine_from_degrees(angle), cosine_from_degrees(angle), 0))

rule "Init menu item positions, num == 2 (PV_P[] = item_positions, PV_T once)":
	set_event(each_player)
	
	add_condition(
		event_player.P == empty_array,
		n_allowed_heroes == 2
	)
	
	add_action(
		set_menu_position(0, -90),
		set_menu_position(1,  90)
	)

rule "Init menu item positions, num > 2 (PV_P[] = item_positions, PV_T once)":
	set_event(each_player)
	
	add_condition(
		event_player.P == empty_array,
		n_allowed_heroes > 2
	)
	
	add_action(
		set_menu_position(event_player.T, event_player.T * (360 / n_allowed_heroes)),
		modify(event_player.T, "add", 1),
		wait(0.016, ignore_condition),
		loop_if(event_player.T < n_allowed_heroes)
	)

rule "Init menu icons (GV_T once)":
	set_event(each_player)
	
	add_condition(
		event_player.A != 0,
		count_of(event_player.P) > 0
	)
	
	visibility = filtered_array(event_player, event_player.R >= 0.1)
	
	def get_icon(i):
		return hero_icon_string(allowed_heroes(event_player)[i])
	
	def get_position(i):
		return world_vector_of(local_vector_of(event_player.A, event_player, rotation) + event_player.P[i] * event_player.R + vector(0, -0.15, 0), event_player, rotation)
	
	def make_text(i):
		return create_in_world_text(visibility, get_icon(i), get_position(i), 2.5, do_not_clip, visible_to_position_and_string)
	
	for i in range(29):
		add_action(
			make_text(i),
			abort_if(n_allowed_heroes < i + 2),
			wait(0.03, ignore_condition)
		)
	add_action(make_text(29))

rule "Open menu (PV_A = menu_center)":
	set_event(each_player)
	
	add_condition(
		interact_pressed == true,
		event_player.R == 0
	)
	
	direction = direction_from_angles(horizontal_facing_angle_of(event_player), min(40, max(-40, vertical_facing_angle_of(event_player))))
	add_action(
		set(event_player.A, eye_pos + 2 * direction),
		set(event_player.R, 0.1),
		chase_player_variable_over_time(event_player, R, 0.2 + 0.028 * n_allowed_heroes, 0.2, destination_and_duration)
	)

rule "Close menu":
	set_event(each_player)
	
	add_condition(
		interact_pressed == false,
		event_player.R > 0
	)
	
	add_action(chase_player_variable_over_time(event_player, R, 0, 0.1, destination_and_duration))

rule "Select menu item (PV_T = selected_item_idx)":
	set_event(each_player)
	
	add_condition(
		interact_pressed == false,
		event_player.R >= 0.2
	)
	
	def switch_to(hero):
		return (
			start_forcing_player_to_be_hero(event_player, hero),
			stop_forcing_player_to_be_hero(event_player)
		)
	
	icon_pos = world_vector_of(local_vector_of(event_player.A, event_player, rotation) + current_array_element * event_player.R, event_player, rotation)
	condition = 10 * (facing_direction_of(event_player) @ direction_towards(eye_pos, icon_pos)) >= 9.98
	selected_icon = first_of(filtered_array(event_player.P, condition))
	value = index_of_array_value(event_player.P, selected_icon)
	add_action(
		set(event_player.T, value),
		switch_to(value_in_array(allowed_heroes(event_player), event_player.T))
	)
