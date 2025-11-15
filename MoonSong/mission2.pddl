(define (problem lunar-mission-2)
    (:domain lunar)

    (:objects
        WP1 - location
        WP2 - location
        WP3 - location
        WP4 - location
        WP5 - location
        WP6 - location
        lander1 - lander
        lander2 - lander
        rover1 - rover
        rover2 - rover
        image1 - image
        image2 - image
        scan1 - scan
        scan2 - scan
        sample1 - sample
        sample2 - sample
    )

    (:init
        (is_connected WP1 WP2)
        (is_connected WP2 WP1)
        (is_connected WP2 WP3)
        (is_connected WP2 WP4)
        (is_connected WP4 WP2)
        (is_connected WP3 WP5)
        (is_connected WP5 WP3)
        (is_connected WP5 WP6)
        (is_connected WP6 WP4)
        (hand_empty rover1)
        (hand_empty rover2)
        (empty_memory rover1)
        (empty_memory rover2)
        (is_landed lander1)
        (on_position lander1 WP2)
        (on_position rover1 WP2)
        (not (is_landed lander2))
        (need_image WP3 image1)
        (need_image WP2 image2)
        (need_scan WP4 scan1)
        (need_scan WP6 scan2)
        (need_sample WP5 sample1)
        (need_sample WP1 sample2)
        (association lander1 rover1)
        (association lander2 rover2)
    )
    (:goal
        (and
            (has_received image1)
            (has_received image2)
            (has_received scan1)
            (has_received scan2)
            (sample_got sample1)
            (sample_got sample2)
        )
    )
)