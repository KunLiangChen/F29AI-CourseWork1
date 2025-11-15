(define (domain lunar)
    (:requirements :strips :typing)

    ; -------------------------------
    ; Types
    ; -------------------------------

    ; EXAMPLE

    ; (:types
    ;     parent_type
    ;     child_type - parent_type

    ; )
    (:types
        equipment
        rover - equipment
        lander - equipment
        location
        data
        scan - data
        image - data
        sample
    )

    ; -------------------------------
    ; Predicates
    ; -------------------------------

    ; EXAMPLE

    ; (:predicates
    ;     (no_arity_predicate)
    ;     (one_arity_predicate ?p - parameter_type)
    ; )

    (:predicates
        (is_landed ?lan - lander) ;Whether a lander is landed or not.
        (on_position ?e - equipment ?l - location) ;Whether an equipment is on a certain location or not.
        (is_connected ?l1 - location ?l2 - location) ;Whether two locations are connected or not.
        (need_image ?l - location ?i - image) ;This location needs take an image
        (need_sample ?l - location ?s - sample) ;This location needs take a sample
        (need_scan ?l - location ?sc - scan) ;This location needs take a scan
        (captured_data ?r - rover ?d - data) ;Rover r has captured data (image,scan).
        (collected_sample ?r - rover ?s - sample) ; Rover r has collected a sample.
        (empty_memory ?r - rover) ;Rover r has empty memory.
        (hand_empty ?r - rover);Rover r has empty hand.
        (is_full ?lan - lander) ;Lander is full with samples
        (has_received ?d - data);Data has been received.
        (sample_got ?s - sample);Sample has been received.
        (association ?lan - lander ?r - rover);Lander is associated with the rover.
    )

    ; -------------------------------
    ; Actions
    ; -------------------------------

    ; EXAMPLE

    ; (:action action-template
    ;     :parameters (?p - parameter_type)
    ;     :precondition (and
    ;         (one_arity_predicate ?p)
    ;     )
    ;     :effect 
    ;     (and 
    ;         (no_arity_predicate)
    ;         (not (one_arity_predicate ?p))
    ;     )
    ; )

    (:action lander_land 
        :parameters (?lan - lander ?r - rover ?l - location)
        :precondition 
        (and
            (not (is_landed ?lan))
            )
        :effect 
        (and
            (is_landed ?lan)
            (on_position ?lan ?l)
            (on_position ?r ?l)
        )
    )
    
    (:action rover_move
        :parameters (?l1 - location ?l2 - location ?r - rover)
        :precondition
        (and
            (not (on_position ?r ?l2))
            (on_position ?r ?l1)
            (is_connected ?l1 ?l2)
        )
        :effect
        (and
            (not (on_position ?r ?l1))
            (on_position ?r ?l2)
        )
    )
    
    (:action take_picture
        :parameters (?r - rover ?l - location ?i - image)
        :precondition
        (and
            (on_position ?r ?l)
            (need_image ?l ?i)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (need_image ?l ?i))
            (captured_data ?r ?i)
        )
    )
    
    (:action take_scan
        :parameters (?r - rover ?l - location ?sc - scan)
        :precondition
        (and
            (on_position ?r ?l)
            (need_scan ?l ?sc)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (need_scan ?l ?sc))
            (captured_data ?r ?sc)
        )   
    )
    
    (:action take_sample
        :parameters (?r - rover ?l - location ?s - sample)
        :precondition
        (and
            (on_position ?r ?l)
            (need_sample ?l ?s)
            (hand_empty ?r)
            
            
        )
        :effect
        (and
            (not (need_sample ?l ?s))
            (not (hand_empty ?r))
            (collected_sample ?r ?s)
        )
    )
    
    (:action transmit_data
        :parameters (?r - rover ?d - data)
        :precondition (and 
            (captured_data ?r ?d)
            (not (has_received ?d))
        ) 
        :effect (and
            (not (captured_data ?r ?d))
            (has_received ?d)
            (empty_memory ?r)
        )
    )
    
    (:action sample_receive
        :parameters (?lan - lander ?r - rover ?s - sample ?l - location)
        :precondition (and
            (not (is_full ?lan))
            (on_position ?r ?l)
            (on_position ?lan ?l)
            (association ?lan ?r)
            (collected_sample ?r ?s)
         )
        :effect (and 
            (is_full ?lan)
            (not (collected_sample ?r ?s))
            (hand_empty ?r)
            (sample_got ?s)
        )
    )
    

        )