# Original by IvanIV
# https://workshop.elohell.gg/kSQZ2iD-_
# Converted to Python by Peppermint#2241

# constants
p_max_effects    = 128
p_paint_cooldown = 0.016

# variables
max_effects = global_X
color_id    = event_player.A
c_text_id   = event_player.B
blobs       = event_player.C
last_index  = event_player.D
removing    = event_player.E

# controls
is_painting = is_button_held(event_player, primary_fire)
is_cycling  = is_button_held(event_player, secondary_fire)
is_undoing  = is_button_held(event_player, ability_2)
is_erasing  = is_button_held(event_player, ultimate)

# shorthands
each_player  = ongoing_each_player(all, all)
everyone     = all_players(team(all))
destroy_blob = destroy_effect(blobs[last_index])

# available colors
colors = [
	white,
	yellow,
	green,
	purple,
	red,
	blue
]

class Color:
	def __init__(self, index):
		self.index = index
		self.color = colors[index]
	
	def hud_rule(self):
		rule str(self.color) + " hud":
			set_event(each_player)
			
			add_condition(color_id == self.index)
			
			add_action(
				create_hud_text(event_player, string("current", null, null, null), null, null, left, 0, self.color, white, white, visible_to_and_string),
				set(c_text_id, last_text_id)
			)
	
	def paint_rule(self):
		rule str(self.color) + " paint":
			set_event(each_player)
			
			add_condition(
				color_id == self.index,
				is_painting == true
			)
			
			switch rollover:
				case last_index >= max_effects:
					set(last_index, 0)
			
			eye_pos = eye_position(event_player)
			position = ray_cast_hit_position(eye_pos, eye_pos + 1000 * facing_direction_of(event_player), everyone, event_player, true)
			
			add_action(
				rollover,
				destroy_blob,
				wait(0.016, ignore_condition),
				create_effect(everyone, orb, self.color, position, 0.1, none),
				set_at_index(blobs, last_index, last_created_entity),
				modify(last_index, "add", 1),
				wait(p_paint_cooldown, ignore_condition),
				loop_if_condition_is_true
			)

rule "init global":
	add_action(set(max_effects, p_max_effects))

rule "init players":
	set_event(each_player)
	
	add_action(
		set_ability_1_enabled(event_player, false),
		set_ability_2_enabled(event_player, false),
		set_ultimate_ability_enabled(event_player, false),
		set_primary_fire_enabled(event_player, false),
		set_secondary_fire_enabled(event_player, false),
		set_status(event_player, null, invincible, 9999)
	)

rule "cycle color":
	set_event(each_player)
	
	add_condition(is_cycling == true)
	
	switch next_color:
		case color_id == 5:
			set(color_id, 0)
		case:
			modify(color_id, "add", 1)
	
	add_action(
		destroy_hud_text(c_text_id),
		next_color
	)

rule "undo":
	set_event(each_player)
	
	add_condition(is_undoing == true)
	
	switch get_last_index:
		case last_index <= 0:
			set(last_index, max_effects - 1)
		case:
			modify(last_index, "subtract", 1)
	
	add_action(
		get_last_index,
		destroy_blob
	)

rule "erase all":
	set_event(each_player)
	
	add_condition(is_erasing == true)
	
	switch set_remove_state:
		case ~removing:
			set(last_index, 0)
			set(removing, true)
	
	add_action(
		set_remove_state,
		destroy_blob,
		modify(last_index, "add", 1),
		wait(0.016, ignore_condition),
		loop_if(last_index < max_effects),
		set(removing, false)
	)

for i in range(len(colors)):
	c = Color(i)
	
	c.hud_rule()
	c.paint_rule()
