import subprocess
import sys
import time


def main():
	command = [
		sys.executable,
		"-m",
		"gunicorn",
		"-w",
		"2",
		"-b",
		"127.0.0.1:5055",
		"--timeout",
		"120",
		"--graceful-timeout",
		"30",
		"--keep-alive",
		"5",
		"app_simple:app",
	]

	while True:
		exit_code = subprocess.call(command)
		print(f"[runner] gunicorn finalizó con código {exit_code}. Reiniciando en 2 segundos...")
		time.sleep(2)


if __name__ == "__main__":
	main()
