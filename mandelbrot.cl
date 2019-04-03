// #pragma OPENCL EXTENSION cl_khr_fp64 : enable

inline bool inRange(float a, float b) {
    return a * a + b * b < 4.0;
}

/* Iterates through the Mandelbrot set at location x,y up to maxTimes */
__kernel void pixel32(__global int* out, const float centerX, const float centerY, const long zoom, const int maxTimes, const float s, const float p, const int sizeX, const int sizeY) {
    // Mandelbrot set is defined as:
    // f(z) = z^2 + c
    // evaluate z = f(z) until abs(z) > 2
    // return numIterations
    // Do this for our current point
    unsigned int x = get_global_id(0);
    unsigned int y = get_global_id(1);

    int times = 2;

    float a = s;
    float b = p;
    float c = (x - sizeX / 2.0) / zoom + centerX;
    float d = (y - sizeY / 2.0) / zoom + centerY;

    while (times < maxTimes && inRange(a, b)) {
        float tmpa = (a*a) - (b*b);
        b = 2*a*b;
        a = tmpa;
        a += c;
        b += d;
        times++;
    }
    out[x * sizeX + y] = times;
}

// Same as pixel32 but double precision
__kernel void pixel64(__global int* out, const double centerX, const double centerY, const long zoom, const int maxTimes, const float s, const float p, const int sizeX, const int sizeY) {
    // Mandelbrot set is defined as:
    // f(z) = z^2 + c
    // evaluate z = f(z) until abs(z) > 2
	// return numIterations 
    // Do this for our current point
    unsigned int x = get_global_id(0);
    unsigned int y = get_global_id(1);

    int times = 0;

    double a = s;
    double b = p;
    double c = (x - sizeX / 2.0) / zoom + centerX;
    double d = (y - sizeY / 2.0) / zoom + centerY;

    while (times < maxTimes && inRange(a, b)) {
        double tmpa = (a*a) - (b*b);
        b = 2*a*b;
        a = tmpa;
        a += c;
        b += d;
        times++;
    }
    out[x * sizeX + y] = times;
}

/*__kernel void pixelHighPrecision(__global int* out, const double centerX, const double centerY, const long zoom, const int maxTimes) {
    // Mandelbrot set is defined as:
    // f(z) = z^2 + c
    // evaluate z = f(z) until abs(z) > 2
    // return numIterations
    // Do this for our current point
    int x = get_global_id(0);
    int y = get_global_id(1);

    int times = 0;

    uint4 a = (uint4) (0, 0, 0, 0);
    uint4 b = (uint4) (0, 0, 0, 0);
    uint4 c
    uint4 d

    while (times < maxTimes && hpInRange(a, b)) {
        int tmpa = ((a*a) >> FPBITSMUL) - ((b*b) >> FPBITSMUL);
        b = 2.0 * ((a*b) >> FPBITSMUL);
        a = tmpa;
        a = a + c;
        b = b + d;
        times++;
    }
    out[x * 600 + y] = times;
}*/

inline unsigned char norm(int in, int min, int max) {
    float x = (float)((float)in - (float)min) * (255.0 / (float)((float)max - (float)min));
    return (char)(16.0 * sqrt(x));
//    return (float)((float)in - (float)min) * (255.0 / (float)((float)max - (float)min));
}

__kernel void color(__global unsigned char* out, __global int* in, const int min, const int max, int sizeX, int sizeY) {
    unsigned int x = get_global_id(0);
    unsigned int y = get_global_id(1);

    unsigned char normalized = norm(in[x * sizeX + y], min, max); // normalized intensity value

/*    out[x * sizeX * 3 + y * 3] = normalized; // set the HUE to normal
    if (normalized == 255) // if normalized value is the largest value, then set saturation to white
        out[x * sizeX * 3 + y * 3 + 1] = 0; // saturation to 0
    else
        out[x * sizeX * 3 + y * 3 + 1] = 255; // saturation to 255
    out[x * sizeX * 3 + y * 3 + 2] = 255; // brightness to 255
*/
    // out[x * sizeX * 3 + y * 3] = 170; // HUE to blue
    out[x * sizeX * 3 + y * 3] = normalized; // HUE to blue
    out[x * sizeX * 3 + y * 3 + 1] = 255; // SATURATION to 255
    if (normalized == 255)  // BRIGHTNESS is 0 if it's the max intensity
	out[x * sizeX * 3 + y * 3 + 2] = 0; 
    else
	out[x * sizeX * 3 + y * 3 + 2] = 255;
	//out[x * sizeX * 3 + y * 3 + 2] = normalized;
}
