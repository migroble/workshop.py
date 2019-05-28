# Original by the one and only Jinko#2838
# https://workshop.elohell.gg/AbJBNOUW0
# Converted to Python by Peppermint#2241
# Incomplete

each_player  = ongoing_each_player(all, all)
player_score = score_of(event_player)
is_scoping   = is_firing_secondary(event_player)
everyone     = all_players(team(all))

class Map:
	def __init__(self, name, id, gimmicks = None):
		self.name = name
		self.id = id
		self.gimmicks = gimmicks if gimmicks is not None else []
	
	def map_condition(self):
		return global_Z == self.id
	
	def create_effects(self):
		conditions = []
		actions = []
		
		conditions.append(self.map_condition())
		
		for gimmick in self.gimmicks:
			if hasattr(gimmick, "create_effect"):
				actions.append(gimmick.create_effect())
		
		return conditions, actions

class JumpPad:
	def __init__(self, name, position, effect_radius, sound_radius, speed, extra_actions = None):
		self.name = name
		self.position = position
		self.effect_radius = effect_radius
		self.trigger_radius = 0.5 + effect_radius
		self.sound_radius = sound_radius
		self.speed = speed
		self.extra_actions = extra_actions
	
	def get_behavior(self):
		conditions = [
			distance_between(event_player, self.position) <= self.trigger_radius,
			is_in_air(event_player) == false
		]
		
		actions = [
			play_effect(everyone, ring_explosion_sound, white, event_player, self.sound_radius),
			apply_impulse(event_player, up, self.speed, to_world, cancel_contrary_motion)
		]
		
		if self.extra_actions is not None:
			actions.extend(self.extra_actions)
		
		return conditions, actions
		
	def create_effect(self):
		return create_effect(everyone, ring, purple, self.position, self.effect_radius, visible_to_position_and_radius)

class Launcher:
	def __init__(self, name, position, target, sound_radius, speed, extra_actions = None):
		self.name = name
		self.position = position
		self.target = target
		self.sound_radius = sound_radius
		self.speed = speed
		self.extra_actions = extra_actions
	
	def get_behavior(self):
		conditions = distance_between(event_player, self.position) <= 1.5
		
		player_velocity = velocity_of(event_player)
		actions = [
			apply_impulse(event_player, -player_velocity, square_root(player_velocity @ player_velocity), to_world, incorporate_contrary_motion),
			set_status(event_player, null, rooted, 0.9),
			apply_impulse(event_player, direction_towards(self.position, self.target), self.speed[0], to_world, cancel_contrary_motion),
			apply_impulse(event_player, up, self.speed[1], to_world, cancel_contrary_motion),
			play_effect(everyone, debuff_impact_sound, white, self.position, self.sound_radius)
		]
		
		if self.extra_actions is not None:
			actions.extend(self.extra_actions)
		
		return conditions, actions
	
	def create_effect(self):
		return create_effect(everyone, good_aura, yellow, self.position, 0.5, visible_to_position_and_radius)

class RestrictedArea:
	def __init__(self, name, position, target, sound_radius, speed):
		self.name = name
		self.position = position
		self.target = target
		self.sound_radius = sound_radius
		self.speed = speed
	
	def get_behavior(self):
		conditions = []
		actions = []
		
		conditions= (distance_between(event_player, self.position[0]) <= 5) | (distance_between(event_player, self.position[1]) <= 6) == true
		
		actions = [
			play_effect(event_player, explosion_sound, white, event_player, self.sound_radius),
			apply_impulse(event_player, vector_towards(event_player, self.target), self.speed, to_world, cancel_contrary_motion),
			apply_impulse(event_player, up, 1, to_world, cancel_contrary_motion),
			small_message(event_player, string("{0} {1}", string("locked", null, null, null), string("zone", null, null, null), null)),
			set_status(event_player, null, knocked_down, 0.016),
			wait(0.5, ignore_condition),
			loop_if_condition_is_true
		]
		
		return conditions, actions

maps = [
	Map("Eichenwalde", 124, [
		JumpPad("Main pad",     vector(46.67,   7.52,  -75.03),  1.85, 25, 23),
		JumpPad("Stairs pad",   vector(60.76,  12.95,  -58.96),  1.3,  15, 20),
		JumpPad("Camper pad",   vector(68,     13.45, -105),     1,    17, 20),
		JumpPad("Elevator pad", vector(95.343, 13.5,   -77.857), 0.75, 15, 15,
						[ set_status(event_player, null, rooted, 0.1) ]),
		Launcher("Platform launcher", vector(93,   19.92, -66.891), vector(34.95,  10.25, -89.7),   40, [ 100, 20 ]),
		Launcher("Cave launcher",     vector(67.51, 5.97, -83.5),   vector(80.501, 13.95, -87.623), 30, [  20, 18 ],
						[ set_player_variable(event_player, D, 1.5), chase_player_variable_at_rate(event_player, D, 0, 1, destination_and_rate) ]),
		RestrictedArea("Restricted area", [ vector(33.351, 14.932, -85.5), vector(32.185, 15.248, -79.729) ], vector(58.779, 19.298, -77.287), 30, 10),
	]),
	Map("Ecopoint Antartica", 18, [
		JumpPad("Mid 1", vector(2.92,  5.58,  3.729), 1, 25, 18),
		JumpPad("Mid 2", vector(2.899, 5.58, -3.351), 1, 25, 18),
		JumpPad("Garage", vector(-15, 7.52, 0), 1, 25, 14),
		Launcher("Launcher right", vector(-2.351, 7.51, 40.71),  vector(-2.351, 8.51, -40.71),  30, [ 25, 17 ]),
		Launcher("Launcher left",  vector(-2.21,  8.52, 39.859), vector(-2.21,  8.52,  39.859), 30, [ 25, 17 ]),
	]),
]

def create_rule_create_effects(map):
	c, a = map.create_effects()
	
	rule "Create all effects - {}".format(map.name):
		set_event(each_player)
		add_condition(c)
		add_action(a)

def create_rule_for_gimmick(map, gimmick):
	c, a = gimmick.get_behavior()
	
	rule gimmick.name:
		set_event(each_player)
		add_condition(map.map_condition())
		
		add_condition(c)
		add_action(a)

for i, map in enumerate(maps):
	create_rule_create_effects(map)
	
	for gimmick in map.gimmicks:
		create_rule_for_gimmick(map, gimmick)