(define (problem lunar-mission-1)
    (:domain lunar)

    (:objects
        rover - rover
        lander - lander
        WP1 - location
        WP2 - location
        WP3 - location
        WP4 - location
        WP5 - location
        image - image
        scan - scan
        sample - sample
    )

    (:init
        (not (is_landed lander))
        (not (is_deployed rover))
        (is_connected WP1 WP2)
        (is_connected WP1 WP4)
        (is_connected WP2 WP3)
        (is_connected WP3 WP5)
        (is_connected WP4 WP3)
        (is_connected WP5 WP1)
        (need_image WP5 image)
        (need_scan WP3 scan)
        (need_sample WP1 sample)
        (empty_memory rover)
        (hand_empty rover)
        (association lander rover)

    )

    (:goal
        (and
            (has_received image)
            (has_received scan)
            (sample_got sample)
        )
    )
)