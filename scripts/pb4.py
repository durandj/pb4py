#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import sys
import tabulate

import pb4py



def add_device_commands(parsers):
	device_parsers = parsers.add_subparsers()

	device_parsers.add_parser(
		'list',
		help = 'List all devices.',
	).set_defaults(func = command_devices_list)



	create_device = device_parsers.add_parser(
		'create',
		help = 'Create a new PushBullet device.',
	)

	create_device.add_argument(
		'name',
		type = str,
		help = 'The name of the device',
	)

	create_device.add_argument(
		'device_type',
		type = str,
		help = 'The type of device (ex: Windows, phone, etc)',
	)

	create_device.set_defaults(func = command_devices_create)



	update_device = device_parsers.add_parser(
		'update',
		help = 'Update an existing PushBullet device.',
	)

	update_device.add_argument(
		'iden',
		type = str,
		help = 'The ID of the device',
	)

	update_device.add_argument(
		'--nickname',
		type    = str,
		default = None,
		help    = 'Set the device nickname',
	)

	update_device.add_argument(
		'--device_type',
		dest    = 'type',
		type    = str,
		default = None,
		help    = 'Set the device type',
	)

	update_device.set_defaults(func = command_devices_update)



	delete_device = device_parsers.add_parser(
		'delete',
		help = 'Delete an existing PushBullet device.',
	)

	delete_device.add_argument(
		'iden',
		type = str,
		help = 'The ID of the device',
	)

	delete_device.set_defaults(func = command_devices_delete)

def add_parser_commands(parsers):
	parsers.add_parser(
		'generate-config',
		help = 'Generate a sane set of config options. These can then bet put in the ~/.pb4pyrc file.',
	).set_defaults(func = command_generate_default_config)

	add_device_commands(parsers.add_parser(
		'devices',
		help = 'Manage connected devices.',
	))

def parse_args():
	parser = argparse.ArgumentParser(
		description = 'A CLI command for working with PushBullet',
	)

	command_parsers = parser.add_subparsers(title = 'commands')
	add_parser_commands(command_parsers)

	return parser.parse_args()



def prompt(question, default = "yes"):
	"""
	Ask a yes/no question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".
	"""

	valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
	if default is None:
		options = ' [y/n] '
	elif default == 'yes':
		options = ' [Y/n] '
	elif default == 'no':
		options = ' [y/N] '
	else:
		raise ValueError('invalid default answer: \'%s\'' % default)

	while True:
		sys.stdout.write(question + options)
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write('Please respond with \'yes\' or \'no\' (or \'y\' or \'n\').\n')

def build_table(data, columns):
	return tabulate.tabulate(
		[
			[row[column] for column in columns]
			for row in data
		],
		[col.capitalize() for col in columns]
	)



def client_command(func):
	def wrapper(*args, **kwargs):
		client = pb4py.Client()

		return func(client, *args, **kwargs)

	return wrapper

def command_generate_default_config(args):
	config = {
		'auth': {
			'type':       'basic',
			'access_token': 'deadbeef',
		},
	}

	print(json.dumps(config, indent = 4, sort_keys = False))

@client_command
def command_devices_list(client, args):
	devices = client.devices()

	print(build_table(devices, ['iden', 'nickname', 'type']))

@client_command
def command_devices_create(client, args):
	client.create_device(args.name, args.device_type)

	print('Device created')

@client_command
def command_devices_update(client, args):
	updates = {
		k: getattr(args, k)
		for k in ['nickname', 'type']
		if getattr(args, k) is not None
	}

	client.update_device(args.iden, updates)

	print('Device updated')

@client_command
def command_devices_delete(client, args):
	device = args.iden
	confirm = prompt('Are you sure you want to delete device {}?'.format(device), default = 'no')
	if not confirm:
		return

	client.delete_device(device)

	print('Device deleted')



def main():
	args = parse_args()

	try:
		args.func(args)
	except Exception as ex:
		print(ex)

if __name__ == '__main__':
	main()

