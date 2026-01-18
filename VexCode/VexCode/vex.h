#pragma once
#include <iostream>
#include "vexlib.h"
using namespace std;

void vexcodeInit(void);

namespace vex {

    enum unit { degrees, radians };
    enum direction { forward, reverse };
#define forward direction::forward
#define reverse direction::reverse

    // Corrected type alias: velocity is an int
    using velocity = int;

    enum velocityUnits { pct, rpm, dps };
#define percent velocityUnits::pct

    enum directionTurn { left, right };
#define vex_left directionTurn::left
#define vex_right directionTurn::right

    enum stopMode { vex_break, vex_coast, vex_hold };

    class DrivetrainClass {
        public:
            explicit DrivetrainClass(int init = 0);
            void setRotation(int degree_value, unit unit_val = degrees);
            void drive(direction dir = forward, velocity vel = 50, velocityUnits unit_val = pct);
            void stop(stopMode mode = vex_break);
            void turn(directionTurn turn = left, velocity vel = 50, velocityUnits unit_val = pct);
            void setDriveVelocity(velocity vel, velocityUnits unit_val = percent);

            int getDegree(void);
            direction getDirection(void);
            velocity getVelocity(void);
        private:
            int degree;
            direction dir;
            velocity vel;
        };

    class motor55 {
        public:
            explicit motor55(int port = 1);
            void spin(direction dir = forward, velocity vel = 50, velocityUnits unit_val = pct);
            void stop(stopMode mode = vex_break);
        private:
            int motorPort;
	};
};

extern class vex::DrivetrainClass Drivetrain;
